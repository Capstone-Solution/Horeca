from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    horeca_server_endpoint = fields.Char(related='company_id.horeca_server_endpoint', string="Horeca Server Endpoint", readonly=False)
    horeca_server_api_token = fields.Char(related='company_id.horeca_server_api_token', string="Horeca Server API Token", readonly=False)
