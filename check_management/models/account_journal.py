# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_check = fields.Boolean(string="Is Check", default=False)
    is_debit = fields.Boolean(string="Is Debit", default=False)
    is_invoice = fields.Boolean(string="Is Invoices", default=False)


class CheckDepoiset(models.TransientModel):
    _name = 'check.depoiset'
    _description = 'Depoiset Journals'

    #
    @api.model
    def _get_custody_id(self):
        check_rec = self.env['payment.check.line'].browse(self._context.get('active_id'))
        return check_rec.custody_id.id

    debit_journal_id = fields.Many2one("account.journal", string="Debit Journal", required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    label = fields.Char(string="Label", required=True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Custody", required=False, default=_get_custody_id)

    # @api.multi
    def action_depoiset(self):
        self.ensure_one()
        x = self._context.get('active_id')
        check_rec = self.env['payment.check.line'].browse(x)
        check_rec.custody_id = self.partner_id.id
        debit_notes_account = check_rec.payment_id.journal_id.default_account_id.id
        check_amount = check_rec.check_amount
        move_line_1 = {
            'account_id': self.debit_journal_id.default_account_id.id,
            'debit': check_amount,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': 0.0,
            'partner_id': check_rec.payment_id.partner_id.id,
            'journal_id': self.debit_journal_id.id,

        }
        move_line_2 = {
            'account_id': debit_notes_account,
            'debit': 0.0,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': check_amount,
            'partner_id': check_rec.payment_id.partner_id.id,
            'journal_id': self.debit_journal_id.id
        }
        lines = [(0, 0, move_line_1), (0, 0, move_line_2)]
        move_vals = {
            'ref': str(self.label) + ' / ' + str(check_rec.check_number),
            'date': self.date,
            'journal_id': self.debit_journal_id.id,
            'line_ids': lines,
        }
        move = self.env['account.move'].create(move_vals)
        if move:
            check_rec.write({'move_ids': [(4, move.id, None)]})
            check_rec.check_under_col = self.debit_journal_id.default_account_id.id
            check_rec.depoiset_journal_id = self.debit_journal_id.id
            check_rec.state = 'depoisted'
        move.action_post()


# accepted btn journals
class CheckAccept(models.TransientModel):
    _name = 'check.accept'
    _description = 'Accept Journals'

    debit_journal_id = fields.Many2one("account.journal", string="Debit Journal", required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    label = fields.Char(string="Label", required=True)

    # @api.multi
    def action_accept(self):
        self.ensure_one()
        x = self._context.get('active_id')
        check_rec = self.env['payment.check.line'].browse(x)
        if check_rec.check_type == 'inbound':
            check_under_col_account = check_rec.depoiset_journal_id.default_account_id.id
            check_amount = check_rec.check_amount
            if check_rec.depoiset_journal_id:
                check_under_col_account = check_rec.depoiset_journal_id.default_account_id.id
            move_line_1 = {
                'account_id': self.debit_journal_id.default_account_id.id,
                'debit': check_amount,
                'name': str(self.label) + ' / ' + str(check_rec.check_number),
                'credit': 0.0,
                'partner_id': check_rec.payment_id.partner_id.id,
                'journal_id': self.debit_journal_id.id
            }
            move_line_2 = {
                'account_id': check_under_col_account,
                'debit': 0.0,
                'name': str(self.label) + ' / ' + str(check_rec.check_number),
                'credit': check_amount,
                'partner_id': check_rec.payment_id.partner_id.id,
                'journal_id': self.debit_journal_id.id
            }
            lines = [(0, 0, move_line_1), (0, 0, move_line_2)]
            move_vals = {
                'ref': str(self.label) + ' / ' + str(check_rec.check_number),
                'date': self.date,
                'journal_id': self.debit_journal_id.id,
                'line_ids': lines,
            }
            move = self.env['account.move'].create(move_vals)
            if move:
                check_rec.write({'move_ids': [(4, move.id, None)]})
                check_rec.state = 'accepted'
                check_rec.check_accept_journal_id = self.debit_journal_id.id
            move.action_post()
        else:
            print("222222222222222222")
            check_under_col_account = check_rec.deduct_journal_id.default_account_id.id
            check_amount = check_rec.check_amount
            if check_rec.depoiset_journal_id:
                check_under_col_account = check_rec.depoiset_journal_id.default_account_id.id
            move_line_1 = {
                'account_id': check_under_col_account,
                'debit': check_amount,
                'name': str(self.label) + ' / ' + str(check_rec.check_number),
                'credit': 0.0,
                'partner_id': check_rec.payment_id.partner_id.id,
                'journal_id': self.debit_journal_id.id
            }
            move_line_2 = {
                'account_id': self.debit_journal_id.default_account_id.id,
                'debit': 0.0,
                'name': str(self.label) + ' / ' + str(check_rec.check_number),
                'credit': check_amount,
                'partner_id': check_rec.payment_id.partner_id.id,
                'journal_id': self.debit_journal_id.id
            }
            lines = [(0, 0, move_line_1), (0, 0, move_line_2)]
            print("5555555555555", lines)
            move_vals = {
                'ref': str(self.label) + ' / ' + str(check_rec.check_number),
                'date': self.date,
                'journal_id': self.debit_journal_id.id,
                'line_ids': lines,
            }
            move = self.env['account.move'].create(move_vals)
            if move:
                check_rec.write({'move_ids': [(4, move.id, None)]})
                check_rec.state = 'accepted'
                check_rec.check_accept_journal_id = self.debit_journal_id.id
            move.action_post()


class RejectedReasons(models.Model):
    _name = 'rejected.reasons'
    _description = 'Rejected Reasons'

    name = fields.Char()


# Reject btn journals
class CheckReject(models.TransientModel):
    _name = 'check.reject'
    _description = 'Reject Journals'

    debit_journal_id = fields.Many2one("account.journal", string="Debit Journal", required=True)
    rejected_reasons_id = fields.Many2one("rejected.reasons", string="Rejected Reasons", required=True)
    notes = fields.Text(string="rejected Reasons")
    date = fields.Date(required=True, default=fields.Date.context_today)
    label = fields.Char(string="Label", required=True)

    # @api.multi
    def action_reject(self):
        self.ensure_one()
        x = self._context.get('active_id')
        check_rec = self.env['payment.check.line'].browse(x)
        debit_notes_account = check_rec.payment_id.journal_id.default_account_id.id
        check_amount = check_rec.check_amount

        move_line_1 = {
            'account_id': debit_notes_account,
            'debit': check_amount,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': 0.0,
            'partner_id': check_rec.payment_id.partner_id.id,
            'journal_id': check_rec.depoiset_journal_id.id
        }
        move_line_2 = {
            'account_id': self.debit_journal_id.default_account_id.id,
            'debit': 0.0,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': check_amount,
            'partner_id': check_rec.payment_id.partner_id.id,
            'journal_id': check_rec.depoiset_journal_id.id
        }
        lines = [(0, 0, move_line_1), (0, 0, move_line_2)]
        move_vals = {
            'ref': str(self.label) + ' / ' + str(check_rec.check_number),
            'date': self.date,
            'journal_id': check_rec.depoiset_journal_id.id,
            'line_ids': lines,
        }
        move = self.env['account.move'].create(move_vals)
        if move:
            check_rec.rejected_notes = self.rejected_reasons_id.name
            check_rec.write({'move_ids': [(4, move.id, None)]})
            check_rec.state = 'rejected'
        move.action_post()


# Deducted btn journals
class CheckDeduct(models.TransientModel):
    _name = 'check.deduct'
    _description = 'Deduct Journals'

    credit_journal_id = fields.Many2one("account.journal", string="Credit Journal", required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    label = fields.Char(string="Label", required=True)

    # @api.multi
    def action_deduct(self):
        self.ensure_one()
        x = self._context.get('active_id')
        check_rec = self.env['payment.check.line'].browse(x)
        check_rec.deduct_journal_id = self.credit_journal_id.id
        check_amount = check_rec.check_amount
        move_line_1 = {
            'account_id': self.credit_journal_id.default_account_id.id,
            'debit': 0.0,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': check_amount,
            'partner_id': check_rec.payment_id.partner_id.id,
            'journal_id': self.credit_journal_id.id
        }
        move_line_2 = {
            'account_id': check_rec.payment_id.journal_id.default_account_id.id,
            'debit': check_amount,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': 0.0,
            'partner_id': check_rec.payment_id.partner_id.id,
            'journal_id': self.credit_journal_id.id
        }
        lines = [(0, 0, move_line_2), (0, 0, move_line_1)]
        move_vals = {
            'ref': str(self.label) + ' / ' + str(check_rec.check_number),
            'date': self.date,
            'journal_id': self.credit_journal_id.id,
            'line_ids': lines,
        }
        move = self.env['account.move'].create(move_vals)
        if move:
            check_rec.write({'move_ids': [(4, move.id, None)]})
            check_rec.state = 'paid_vendor'
        move.action_post()


# Deducted Transfer
class TransferDeduct(models.TransientModel):
    _name = 'transfer.deduct'
    _description = 'Deduct Transfer'

    bank_journal_id = fields.Many2one("account.journal", string="Bank Journal", required=True)
    cash_journal_id = fields.Many2one("account.journal", string="Cash Journal", required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    label = fields.Char(string="Label", required=True)

    # @api.multi
    def action_transfer_deduct(self):
        self.ensure_one()
        x = self._context.get('active_id')
        check_rec = self.env['payment.check.line'].browse(x)
        check_amount = check_rec.check_amount
        move_line_1 = {
            'account_id': check_rec.payment_id.destination_journal_id.default_account_id.id,
            'debit': 0.0,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': check_amount,
            'journal_id': self.cash_journal_id.id
        }
        move_line_2 = {
            'account_id': self.cash_journal_id.default_account_id.id,
            'debit': check_amount,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': 0.0,
            'journal_id': self.cash_journal_id.id
        }
        lines = [(0, 0, move_line_2), (0, 0, move_line_1)]
        move_vals = {
            'ref': str(self.label) + ' / ' + str(check_rec.check_number),
            'date': self.date,
            'journal_id': self.cash_journal_id.id,
            'line_ids': lines,
        }
        move1 = self.env['account.move'].create(move_vals)
        if move1:
            check_rec.write({'move_ids': [(4, move1.id, None)]})
        move1.action_post()

        move_line_3 = {
            'account_id': self.bank_journal_id.default_account_id.id,
            'debit': 0.0,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': check_amount,
            'journal_id': self.bank_journal_id.id
        }
        move_line_4 = {
            'account_id': check_rec.payment_id.journal_id.default_account_id.id,
            'debit': check_amount,
            'name': str(self.label) + ' / ' + str(check_rec.check_number),
            'credit': 0.0,
            'journal_id': self.bank_journal_id.id
        }
        lines = [(0, 0, move_line_4), (0, 0, move_line_3)]
        move_vals = {
            'ref': str(self.label) + ' / ' + str(check_rec.check_number),
            'date': self.date,
            'journal_id': self.bank_journal_id.id,
            'line_ids': lines,
        }
        move2 = self.env['account.move'].create(move_vals)
        if move2:
            check_rec.write({'move_ids': [(4, move2.id, None)]})
            check_rec.state = 'complete_transfer'
        move2.action_post()
