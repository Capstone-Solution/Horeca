# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class Violations(models.Model):
    _name = 'violations'
    _description = 'violations Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]


    state = fields.Selection([("draft", "Draft"),
                              ("financial_manager", "Financial Manager"),
                              ("general_manager", "General Manager"),
                              ("confirm", "Confirmed"),
                              ("paid", "Paid"),
                              ("reconcile", "Reconcile"),
                              ("rejected", "Rejected")],
                             readonly=True,
                             default="draft",
                             tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    no_of_installment = fields.Integer(string="No Of Installment", tracking=True, default=1)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    violations_ids = fields.One2many('violations.line', 'violations_id_line')
    journal_id = fields.Many2one('account.journal', string='Journal',)
    account_id = fields.Many2one('account.account', string='Debit Account',)
    account_idd = fields.Many2one('account.account', string='Credit Account')

    journal_id_reconcile_amount = fields.Many2one('account.journal', string='Journal', tracking=True)
    debit_reconcile_amount = fields.Many2one('account.account', string='Debit Account', tracking=True)
    credit_reconcile_amount = fields.Many2one('account.account', string='Credit Account', tracking=True)

    loan_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    journal_entry_id_for_reconcile = fields.Many2one('account.move', string='', copy=False, readonly=True)
    type = fields.Many2one('type.loan.advance')

    def unlink(self):
        error_message = _('You cannot delete a violations which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.user_has_groups('base.group_user'):
            if any(hol.state not in ['draft', 'rejected'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(Violations, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('violations') or 'New'
        result = super(Violations, self).create(vals)
        return result

    def action_compute(self):
        for rec in self:
            list = []
            count = 0
            loan_line = []
            for line in rec.violations_ids:
                if not line.is_created:
                    if not line.delay:
                        list.append(line.name)
                    else:
                        count += 1
                        line.is_created = True
            max_date = max(list)
            new_date = max_date + relativedelta(months=1)
            for i in range(count):
                loan_line.append((0, 0, {
                    'name': new_date,
                    'amount': rec.amount / rec.no_of_installment,
                }))
                new_date = new_date + relativedelta(months=1)

            rec.violations_ids = loan_line

    def compute_installment(self):
        for rec in self:
            loan_line = []
            no_install = rec.no_of_installment
            rec.violations_ids = False
            date_date = rec.deduction_date
            for line in range(no_install):
                loan_line.append((0, 0, {
                    'name': date_date,
                    'amount': rec.amount / rec.no_of_installment,
                }))
                date_date = date_date + relativedelta(months=1)
            rec.violations_ids = loan_line

    def validate_action(self):
        for rec in self:
            rec.state = 'financial_manager'

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def financial_manager(self):
        for rec in self:
            rec.state = 'general_manager'

    def general_manager(self):
        for rec in self:
            rec.state = 'confirm'

    employees_customs_analytics_id = fields.Many2one('employee.analytic.report', string="Employee Analytic",
                                                     related='employee_id.employee_custom_analytic_id')

    def paid(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'ref': rec.name,
                'date': rec.deduction_date,
                'journal_id': self.journal_id.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.account_id.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount,
                    'employee_analytic_id': rec.employees_customs_analytics_id.id,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.state = 'paid'

    amount_not_paid = fields.Float(string="amount not paid", compute='_compute_amount_not_paid')

    @api.depends('violations_ids')
    def _compute_amount_not_paid(self):
        for rec in self:
            rec.amount_not_paid = 0
            if rec.violations_ids:
                amount_not_p = 0
                for i in rec.violations_ids:
                    if i.is_paid == False:
                        amount_not_p += i.amount
                rec.amount_not_paid = amount_not_p

    def reconcile_amount(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'entry',
                'ref': rec.name,
                'date': rec.deduction_date,
                'journal_id': self.journal_id_reconcile_amount.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.debit_reconcile_amount.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount_not_paid,
                    'employee_analytic_id': rec.employees_customs_analytics_id.id,
                }), (0, 0, {
                    'account_id': rec.credit_reconcile_amount.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount_not_paid,
                })],
            })
            rec.journal_entry_id_for_reconcile = invoice.id
            rec.state = 'reconcile'
            if rec.violations_ids:
                for l in rec.violations_ids:
                    l.is_paid = True

    def rejected(self):
        for rec in self:
            rec.state = 'rejected'

    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def _check_exist_employee_id(self):
        print('_check_exist_employee_id')
        for sc in self:
            violations = self.env['violations'].search([('employee_id', '=', sc.employee_id.id), ('state', '=', 'paid'),
                                              ('violations_ids', '!=', False)])
            if violations:
                the_loan_is_not_paid = violations.violations_ids.filtered(lambda violation: violation.is_paid != True)
                print('the_loan_is_not_paid', the_loan_is_not_paid)
                if the_loan_is_not_paid:
                    raise ValidationError("Please pay all installments for this employee's first")
                else:
                    continue
            else:
                continue

    # employee_number_for_loan = fields.Char(string="Employee Number", related='employee_id.employee_number')
    employee_number_for_loan = fields.Char(string="Employee Number")
    identification_for_loan = fields.Char(string="Identification No", related='employee_id.identification_id',)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.company,)


class ViolationsLine(models.Model):
    _name = 'violations.line'
    _description = 'violations_line'


    name = fields.Date('Payment Date')
    amount = fields.Float('Amount')
    violations_payslip_id = fields.Many2one('hr.payslip', string='')
    violations_id_line = fields.Many2one('violations', string='')
    delay = fields.Boolean()
    is_created = fields.Boolean()
    is_paid = fields.Boolean(string='In payslip', readonly=True)
