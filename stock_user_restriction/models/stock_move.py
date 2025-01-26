# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, api, _
from odoo.exceptions import AccessError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.one
    @api.constrains("state", "location_id", "location_dest_id")
    def check_user_location_restriction(self):
        if self.state not in ["done", "cancel"]:
            return True

        if self.env.user.location_restriction:
            message = _(
                "Invalid Location.\n"
                "You cannot process this move since you do not control "
                "the location '%s'.\n"
                "Please contact your Adminstrator."
            )
            location_done_ids = self.env.user.location_done_ids

            if self.state in ["done"]:
                if self.location_id not in location_done_ids:
                    raise AccessError(message % self.location_id.display_name)
                elif self.location_dest_id not in location_done_ids:
                    raise AccessError(message % self.location_dest_id.display_name)

            location_cancel_ids = self.env.user.location_cancel_ids

            if self.state in ["cancel"]:
                if self.location_id not in location_cancel_ids:
                    raise AccessError(message % self.location_id.display_name)
                elif self.location_dest_id not in location_cancel_ids:
                    raise AccessError(message % self.location_dest_id.display_name)
