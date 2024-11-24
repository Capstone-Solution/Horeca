# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_reference = fields.Char()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    application_price = fields.Float()
