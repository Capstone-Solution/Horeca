import requests
from odoo import models, fields, api, _
import logging
import json

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            self.send_post_request_to_horeca_server(order)
        return res

    def send_post_request_to_horeca_server(self, order):
        company = self.env.company
        url = company.horeca_server_endpoint
        api_token = company.horeca_server_api_token

        if not url or not api_token:
            _logger.error("Horeca server endpoint or API token is not set.")
            return

        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

        total_discount = sum(line.price_unit * line.product_uom_qty  for line in order.order_line if line.price_subtotal<0)
        print(total_discount)
        details = [{
            'product_refrence': line.product_id.default_code,
            'product_id': line.product_id.product_tmpl_id.id,
            'quantity': line.product_uom_qty,
            'total': line.price_subtotal
        } for line in order.order_line if line.price_subtotal > 0]

        data = {
            # 'user_id': 4218,
            'user_id': order.partner_id.id,
            'application_order_reference': order.order_reference or "NO_REF",
            'total_amount': order.amount_total,
            'total': order.amount_total,
            'odoo_reference': order.name,
            'discount': - total_discount,
            'notes': order.note or '',
            'details': details,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            # print(response.json())
            txt = "Order was synchronized Successfully "

            order.message_post(body=txt, message_type="comment")

        except requests.exceptions.RequestException as e:
            order.message_post(body=e, message_type="comment")
            err_txt = json.loads(e.response.text)
            order.message_post(body=err_txt["message_en"], message_type="comment")

            _logger.error(f"API Integeration Error Failed to send POST request to Horeca server: {e}")
            # You might want to handle the error more gracefully here.
