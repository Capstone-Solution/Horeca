from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    horeca_server_endpoint = fields.Char(string="Horeca Server Endpoint")
    horeca_server_api_token = fields.Char(string="Horeca Server API Token")
