# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_boolean = fields.Boolean(string='Price unite boolean', default=True, compute='_compute_check_readonly',
                                        help="This field check whether readonly for user on not ")

    discount_boolean = fields.Boolean(string='Discount boolean',  default=True, compute='_compute_check_readonly',
                                      help="This field check whether readonly for user on not ")

    def _compute_check_readonly(self):
        for rec in self:
            rec.price_unit_boolean = rec.env.user.readonly_unit_price_sales
            rec.discount_boolean = rec.env.user.readonly_discount_sales
