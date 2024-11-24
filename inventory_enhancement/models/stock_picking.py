from odoo import api, models


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('location_id', 'location_dest_id')
    def _onchange_locations(self):
        (self.move_ids | self.move_ids_without_package).update({
            "location_id": self.location_id,
            "location_dest_id": self.location_dest_id
        })
        if self._origin.location_id != self.location_id and any(line.quantity for line in self.move_ids.move_line_ids):
            print("========== Stop warning ")
            # return {'warning': {
            #     'title': 'Locations to update',
            #     'message': _("You might want to update the locations of this transfer's operations")
            # }}
