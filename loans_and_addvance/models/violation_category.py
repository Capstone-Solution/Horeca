from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ViolationCategory(models.Model):
    _name = 'violation.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    max_number = fields.Integer()
    violation_category_ids = fields.One2many('violation.category.line', 'violation_category_id')

    @api.onchange('max_number')
    def _onchange_max_number(self):
        if self.max_number:
            # Clear existing lines to reset them according to the new max_number
            self.violation_category_ids = [(5, 0, 0)]  # This command removes all existing records from the set
            # Create new lines with incremental action_number
            new_lines_commands = []
            for i in range(1, self.max_number + 1):
                new_line_command = (0, 0, {'action_number': i, 'action': '', 'deduction_percentage': 0})
                new_lines_commands.append(new_line_command)
            self.violation_category_ids = new_lines_commands


class ViolationCategoryLine(models.Model):
    _name = 'violation.category.line'

    action_number = fields.Integer()
    action = fields.Char()
    deduction_percentage = fields.Integer()
    violation_category_id = fields.Many2one('violation.category')


class PenaltyViolation(models.Model):
    _name = 'penalty.violation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(tracking=True, readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending Approval'), ('approve', 'Approved'), ('cancel', 'Cancelled')],
        default='draft', tracking=True)
    employee_id = fields.Many2one('hr.employee', tracking=True)
    date = fields.Date(tracking=True)
    occurrence_count = fields.Integer(tracking=True)
    violation_category = fields.Many2one('violation.category', tracking=True)
    violation_action = fields.Char(tracking=True, compute='get_violation_action')
    violation_amount = fields.Float(tracking=True, compute='get_violation_amount', store=True, readonly=False)
    number_of_days = fields.Integer(default='1')
    category_specified = fields.Boolean()

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('penalty.violation') or 'new'
        return super(PenaltyViolation, self).create(vals)

    @api.depends('violation_category', 'occurrence_count')
    def get_violation_action(self):
        for rec in self:
            if rec.violation_category and rec.category_specified:
                rec.violation_action = rec.violation_category.violation_category_ids.filtered(
                    lambda x: x.action_number == rec.occurrence_count).action
            else:
                rec.violation_action = ''

    @api.depends('violation_category', 'occurrence_count', 'number_of_days')
    def get_violation_amount(self):
        for rec in self:
            if rec.violation_category and rec.category_specified:
                violation_amount = rec.violation_category.violation_category_ids.filtered(
                    lambda x: x.action_number == rec.occurrence_count).deduction_percentage
                if rec.employee_id.contract_id and rec.number_of_days:
                    rec.violation_amount = violation_amount * (
                            rec.employee_id.contract_id.wage / 30) / 100 * rec.number_of_days
                else:
                    rec.violation_amount = 0
            else:
                rec.violation_amount = 0

    def action_pending(self):
        self.state = 'pending'

    def action_approve(self):
        self.state = 'approve'

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'
