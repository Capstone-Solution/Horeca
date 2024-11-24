# -*- coding: utf-8 -*-

import base64
import io
from odoo import models


class SaleLineXlsx(models.AbstractModel):
    _name = 'report.sale_enhancement.report_sale_line_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, sales_orders):
        # print("========== sales_orders ", sales_orders)
        # print("========== Data ", data)
        header_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        data_format = workbook.add_format({'font_size': 10, 'align': 'vcenter'})

        # active_ids = self._context.get('active_ids', [])
        # print("active_ids ", active_ids)

        sheet = workbook.add_worksheet('Sale')

        # sales = self.env['sale.order'].browse(sales_orders)
        # print("============ sales ", sales)

        # Report Header
        sheet.write(0, 0, 'Order Reference', header_format)
        sheet.write(0, 1, 'Customer', header_format)
        sheet.write(0, 2, 'City', header_format)
        sheet.write(0, 3, 'Street_1', header_format)
        sheet.write(0, 4, 'Mobile', header_format)
        sheet.write(0, 5, 'Phone', header_format)
        sheet.write(0, 6, 'Total', header_format)
        sheet.write(0, 7, 'Sales Person', header_format)

        row = 1
        col = 0

        # Report Body
        for sale in sales_orders:
            sheet.write(row, 0, sale.name, data_format)
            sheet.write(row, 1, sale.partner_id.name, data_format)
            sheet.write(row, 2, sale.partner_id.city, data_format)
            sheet.write(row, 3, sale.partner_id.street, data_format)
            sheet.write(row, 4, sale.partner_id.mobile, data_format)
            sheet.write(row, 5, sale.partner_id.phone, data_format)
            sheet.write(row, 6, sale.amount_total, data_format)
            sheet.write(row, 7, sale.user_id.name, data_format)

            row += 1



