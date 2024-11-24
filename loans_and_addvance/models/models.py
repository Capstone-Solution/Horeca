# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class LoansAndAddvance(models.Model):
    _name = 'loans'
    _description = 'loans_Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # @api.model
    # def get_journal(self):
    #     journal = self.env['account.journal'].sudo().search([('is_loan', '=', True)], limit=1).id
    #     return journal

    state = fields.Selection([("draft", "Draft"),
                              ("financial_manager", "Financial Manager"),
                              ("general_manager", "General Manager"),
                              ("confirm", "Confirmed"),
                              ("paid", "Paid"),
                              ("paid2", "To Reconcile"),
                              ("reconcile", "Reconcile"),
                              ("rejected", "Rejected")],
                             readonly=True,
                             default="draft",
                             tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True, default=fields.Date.today)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True, default=fields.Date.today)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    no_of_installment = fields.Integer(string="No Of Installment", tracking=True, default=1)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    loans_ids = fields.One2many('loans.line', 'loans_id', string="",)
    # reason = fields.Text(string="Reason", tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal',)
    account_id = fields.Many2one('account.account', string='Debit Account',)
    account_idd = fields.Many2one('account.account', string='Credit Account')

    journal_id_reconcile_amount = fields.Many2one('account.journal', string='Journal', tracking=True)
    debit_reconcile_amount = fields.Many2one('account.account', string='Debit Account', tracking=True)
    credit_reconcile_amount = fields.Many2one('account.account', string='Credit Account', tracking=True)

    loan_id = fields.Many2one('hr.payslip', string='')
    type = fields.Many2one('type.loan.advance')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    journal_entry_id_for_reconcile = fields.Many2one('account.move', string='', copy=False, readonly=True)

    def unlink(self):
        error_message = _('You cannot delete a loans which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.user_has_groups('base.group_user'):
            if any(hol.state not in ['draft', 'rejected'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(LoansAndAddvance, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('loans.loane') or 'New'
        result = super(LoansAndAddvance, self).create(vals)
        return result

    # @api.depends('journal_id')
    # def git_account_id_idd(self):
    #     for rec in self:
    #         rec.account_id = False
    #         rec.account_idd = False
    #         if rec.journal_id.account_ids and rec.journal_id.account_idd:
    #             rec.account_id = rec.journal_id.account_ids.id
    #             rec.account_idd = rec.journal_id.account_idd.id
    #         else:
    #             rec.account_id = False
    #             rec.account_idd = False

    def paid2(self):
        for rec in self:
            rec.state = 'paid2'
    def action_compute(self):
        for rec in self:
            list = []
            count = 0
            loan_line = []
            for line in rec.loans_ids:
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

            rec.loans_ids = loan_line

    def compute_installment(self):
        for rec in self:
            loan_line = []
            no_install = rec.no_of_installment
            rec.loans_ids = False
            date_date = rec.deduction_date
            for line in range(no_install):
                loan_line.append((0, 0, {
                    'name': date_date,
                    'amount': rec.amount / rec.no_of_installment,
                }))
                date_date = date_date + relativedelta(months=1)
            rec.loans_ids = loan_line

    def validate_action(self):
        for rec in self:
            rec.state = 'financial_manager'
        self.compute_installment()

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
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount,
                    'employee_analytic_id': rec.employees_customs_analytics_id.id,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.journal_entry_id.action_post()
            rec.state = 'paid'


    amount_not_paid = fields.Float(string="amount not paid", compute='_compute_amount_not_paid')

    @api.depends('loans_ids')
    def _compute_amount_not_paid(self):
        for rec in self:
            rec.amount_not_paid = 0
            if rec.loans_ids:
                amount_not_p = 0
                for i in rec.loans_ids:
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
            if rec.loans_ids:
                for l in rec.loans_ids:
                    l.is_paid = True


    def rejected(self):
        for rec in self:
            rec.state = 'rejected'


    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def _check_exist_employee_id(self):
        print('_check_exist_employee_id')
        for sc in self:
            loans = self.env['loans'].search([('employee_id', '=', sc.employee_id.id), ('state', '=', 'paid'),
                                              ('loans_ids', '!=', False)])
            if loans:
                the_loan_is_not_paid = loans.loans_ids.filtered(lambda loan: loan.is_paid != True)
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

# loan model
class LoansAddvanceLine(models.Model):
    _name = 'loans.line'
    _description = 'loans_line'

    name = fields.Date('Payment Date')
    amount = fields.Float('Amount')
    loans_payslip_id = fields.Many2one('hr.payslip', string='')
    loans_id = fields.Many2one('loans', string='')
    delay = fields.Boolean()
    is_created = fields.Boolean()
    is_paid = fields.Boolean(string='In payslip', readonly=True)
    # readonly = True

    @api.onchange('delay')
    def get_checkbox_match(self):
        for rec in self:
            rec.is_paid = rec.delay



# salary advance model
class EditSalaryAdvance(models.Model):
    _name = 'salary.advance'
    _description = 'salary advance Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def get_journal(self):
        journal = self.env['account.journal'].sudo().search([('is_salary_advance', '=', True)], limit=1).id
        return journal

    state = fields.Selection([("draft", "Draft"),
                              ("financial_manager", "Financial Manager"),
                              ("general_manager", "General Manager"),
                              ("confirm", "Confirmed"),
                              ("paid", "Paid"),
                              ("rejected", "Rejected")],
                             readonly=True,
                             default="draft",
                             tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True, default=fields.Date.today)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True, default=fields.Date.today)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')

    journal_id = fields.Many2one('account.journal', string='Journal',)
    account_id = fields.Many2one('account.account', string='Debit Account',)
    account_idd = fields.Many2one('account.account', string='Credit Account')

    # journal_id = fields.Many2one('account.journal', string='Journal', default=get_journal)
    # account_id = fields.Many2one('account.account', string='Debit Account', compute='git_account_id_idd')
    # account_idd = fields.Many2one('account.account', string='Credit Account', compute='git_account_id_idd')
    reason = fields.Text(string="Reason", tracking=True)
    salary_advance_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)
    type = fields.Many2one('type.loan.advance')

    def unlink(self):
        error_message = _('You cannot delete a Advance which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.user_has_groups('base.group_user'):
            if any(hol.state not in ['draft', 'rejected'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(EditSalaryAdvance, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('salary.advance') or 'New'
        result = super(EditSalaryAdvance, self).create(vals)
        return result

    @api.depends('journal_id')
    def git_account_id_idd(self):
        for rec in self:
            rec.account_id = False
            rec.account_idd = False
            if rec.journal_id.account_ids and rec.journal_id.account_idd:
                rec.account_id = rec.journal_id.account_ids.id
                rec.account_idd = rec.journal_id.account_idd.id
            else:
                rec.account_id = False
                rec.account_idd = False

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

    emp_customs_analytic_id = fields.Many2one('employee.analytic.report', string="Employee Analytic",
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
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount,
                    'employee_analytic_id': rec.emp_customs_analytic_id.id,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.journal_entry_id.action_post()
            rec.state = 'paid'

    def rejected(self):
        for rec in self:
            rec.state = 'rejected'

    @api.onchange('amount')
    def _onchange_amount(self):
        # print('_onchange_amount')
        for rec in self:
            if rec.employee_id:
                hr_contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id),
                                                           ('state', '=', 'open')],limit=1)
                # print('hr_contract', hr_contract)
                # if rec.amount > hr_contract.total_salary:
                #     raise ValidationError(_('Please change the amount to be less than the total salary %s %s.'%(hr_contract.total_salary, '$')))


    # employee_number_for_advance = fields.Char(string="Employee Number", related='employee_id.employee_number')
    employee_number_for_advance = fields.Char(string="Employee Number")
    identification_for_advance = fields.Char(string="Identification No", related='employee_id.identification_id',)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True,
                                 default=lambda self: self.env.company,)

class HrPaysLipInherit(models.Model):
    _inherit = 'hr.payslip'

    loans_line_ids = fields.One2many(comodel_name="loans.line", inverse_name="loans_payslip_id",
                                     required=False, compute='get_loan_ids')

    violations_line_ids = fields.One2many(comodel_name="violations.line", inverse_name="violations_payslip_id",
                                          required=False, compute='get_violations_line_ids')
    violations = fields.Float(string="violations", compute='get_violations_line_ids')
    total_unpaid_violations= fields.Float(string="Total unpaid Violations", compute='get_violations_line_ids')


    loans = fields.Float(string="Loans", compute='get_loan_ids')
    total_unpaid_loans = fields.Float(string="Total unpaid loans", compute='get_loan_ids')
    salary_advance_ids = fields.One2many(comodel_name="salary.advance", inverse_name="salary_advance_id", string="",
                                         required=False, compute='get_salary_advance_ids')
    salary_advance = fields.Float(string="Salary Advance", compute='get_salary_advance_ids')
    car_loans = fields.Float(string="Car Loans", required=False, )
    other_loans = fields.Float(string="Other Loans", required=False, )

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_violations_line_ids(self):
        self.violations_line_ids = False
        self.violations = 0
        for rec in self:
            violations = self.env['violations'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('violations_ids', '!=', False),
            ])
            amount = 0
            for l in violations.violations_ids:
                if l.is_paid == False:
                    amount += l.amount
            rec.total_unpaid_violations = amount
            if violations:
                rec.violations_line_ids = violations.violations_ids.filtered(lambda v: v.name >= rec.date_from and v.name <= rec.date_to and v.delay != True and v.is_created != True).ids
                rec.violations = sum(list(rec.violations_line_ids.mapped('amount'))) if rec.violations_line_ids else 0


    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_loan_ids(self):
        self.loans_line_ids = False
        self.loans = 0
        for rec in self:
            loans = self.env['loans'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('loans_ids', '!=', False),
            ])
            amount = 0
            for l in loans.loans_ids:
                if l.is_paid == False:
                    amount += l.amount
                # rec.total_unpaid_loans = amount
            rec.total_unpaid_loans = amount
            if loans:
                rec.loans_line_ids = loans.loans_ids.filtered(lambda loan: loan.name >= rec.date_from and loan.name <= rec.date_to and loan.delay != True and loan.is_created != True).ids
                rec.loans = sum(list(rec.loans_line_ids.mapped('amount'))) if rec.loans_line_ids else 0


    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_salary_advance_ids(self):
        for rec in self:
            rec.salary_advance_ids = False
            salary_advance = self.env['salary.advance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('deduction_date', '<=', rec.date_to),
                ('deduction_date', '>=', rec.date_from),
            ])
            if salary_advance:
                for rec in rec:
                    rec.salary_advance_ids = salary_advance
            else:
                rec.salary_advance_ids = False
            rec.salary_advance = sum(rec.salary_advance_ids.mapped('amount')) if rec.salary_advance_ids else 0


    def action_payslip_paid(self):
        print('action_payslip_paid')
        res = super(HrPaysLipInherit, self).action_payslip_paid()
        for rec in self:
            loans = self.env['loans'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('loans_ids', '!=', False),
            ])
            if loans:
                the_line = loans.loans_ids.filtered(lambda loan: loan.name >= rec.date_from and loan.name <= rec.date_to and
                                                                 loan.delay != True and loan.is_created != True and
                                                                 loan.is_paid != True)
                print('the_line', the_line)
                if the_line:
                    if rec.state == 'paid':
                        print('rec.state ', rec.state )
                        the_line.is_paid = True
                # print('the_line.is_paid==', the_line.is_paid)
            violations = self.env['violations'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('violations_ids', '!=', False),
            ])
            if violations:
                the_violations = violations.violations_ids.filtered(lambda v: v.name >= rec.date_from and v.name <= rec.date_to and
                                                                                       v.delay != True and v.is_created != True and v.is_paid != True)
                if the_violations:
                    if rec.state == 'paid':
                        the_violations.is_paid = True


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    is_loan = fields.Boolean(string="Is Loan", )
    is_salary_advance = fields.Boolean(string="Is Salary Advance", )
    account_ids = fields.Many2one('account.account', string='Debit Account', )
    account_idd = fields.Many2one('account.account', string='Credit Account', )
