# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, _
from odoo.tools import float_utils


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _generate_moves(self):
        diff_lines = self.filtered(
            lambda l: float_utils.float_compare(
                l.theoretical_qty,
                l.product_qty,
                precision_rounding=l.product_id.uom_id.rounding,
            )
            != 0
        )
        usual_lines = self
        split_invetory_id = False

        for line in diff_lines:
            diff = float_utils.float_compare(
                line.theoretical_qty - line.product_qty,
                0.0,
                precision_rounding=line.product_uom_id.rounding,
            )

            if (diff < 0 and line.inventory_id.split_missing) or (
                diff > 0 and line.inventory_id.split_surpluses
            ):
                if not split_invetory_id:
                    split_invetory_id = self.env["stock.inventory"].create(
                        {
                            "name": line.inventory_id.name + _(" - SPLITTED"),
                            "state": "confirm",
                            "location_id": line.inventory_id.location_id.id,
                            "filter": line.inventory_id.filter,
                        }
                    )

                usual_lines -= line
                line.inventory_id = split_invetory_id

        return super(StockInventoryLine, usual_lines)._generate_moves()
