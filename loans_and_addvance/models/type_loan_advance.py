# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TypeLoanAdvance(models.Model):
  _name = 'type.loan.advance'
  _description = 'Type'
  _inherit = ["mail.thread", "mail.activity.mixin"]


  name = fields.Char(string="Name", required=True, tracking=True)
