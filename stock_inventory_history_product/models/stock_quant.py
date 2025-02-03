# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out
        )
        line = res["move_line_ids"][0][2]
        line["previous_inventory_quantity"] = self.quantity
        line["counted_inventory_quantity"] = self.inventory_quantity

        return res

    def _apply_inventory(self):
        res = super()._apply_inventory()
        move_line_obj = self.env["stock.move.line"]

        for record in self:
            move_line_ids = move_line_obj.search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("lot_id", "=", record.lot_id.id),
                    ("inventory_adjustment_id", "=", record.current_inventory_id.id),
                    "|",
                    ("location_id", "=", record.location_id.id),
                    ("location_dest_id", "=", record.location_id.id),
                ]
            )

            for move_line_id in move_line_ids:
                move_line_id.product_id.last_inventory_date = move_line_id.date

        return res
