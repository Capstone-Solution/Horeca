from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    location_id = fields.Many2one(
        'stock.location', 'From', domain="[('usage', '!=', 'view')]", check_company=True,
        required=True, compute="_compute_location_id", store=True, readonly=False, precompute=True)
    location_dest_id = fields.Many2one('stock.location', 'To', check_company=True, required=True,
                                       domain="[('usage', '!=', 'view')]", compute="_compute_location_id", store=True,
                                       readonly=False, precompute=True)

    @api.depends('move_id', 'move_id.location_id', 'move_id.location_dest_id')
    def _compute_location_id(self):
        for line in self:
            if line.location_id:
                # print("============= Check ")
                line.location_id = line.move_id.location_id or line.picking_id.location_id
            if line.location_dest_id:
                # print("============= Check Two ")
                line.location_dest_id = line.move_id.location_dest_id or line.picking_id.location_dest_id
