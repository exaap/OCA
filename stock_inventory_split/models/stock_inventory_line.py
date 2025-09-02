# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, _
from odoo.tools import float_utils


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _generate_moves(self):
        line_ids = self.env["stock.inventory.line"]
        split_invetory_id = False

        for line_id in self:
            diff = float_utils.float_compare(
                line_id.theoretical_qty - line_id.product_qty,
                0.0,
                precision_rounding=line_id.product_uom_id.rounding,
            )

            if (diff < 0 and line_id.inventory_id.split_missing) or (
                diff > 0 and line_id.inventory_id.split_surpluses
            ):
                if not split_invetory_id:
                    split_invetory_id = self.env["stock.inventory"].create(
                        {
                            "name": line_id.inventory_id.name + _(" - RECOUNT"),
                            "state": "confirm",
                            "location_id": line_id.inventory_id.location_id.id,
                            "filter": line_id.inventory_id.filter,
                        }
                    )

                line_id.inventory_id = split_invetory_id
            else:
                line_ids += line_id

        return super(StockInventoryLine, line_ids)._generate_moves()
