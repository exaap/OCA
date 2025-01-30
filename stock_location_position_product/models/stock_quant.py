# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    initial_position = fields.Char(string="Initial Position")
    final_position = fields.Char(string="Final Position")

    def write(self, vals):
        res = super(StockQuant, self).write(vals)
        initial_position = vals.get("initial_position")
        final_position = vals.get("final_position")

        if not initial_position and not final_position:
            return res

        location_position_obj = self.env["stock.location.position"]
        location_position_id = location_position_obj.search(
            [
                "&",
                ("product_template_id", "=", self.product_id.product_tmpl_id.id),
                ("stock_location_id", "=", self.location_id.id),
            ]
        )

        if location_position_id:
            initial_position = initial_position or location_position_id.initial_position
            final_position = final_position or location_position_id.final_position

            if (
                location_position_id.initial_position != initial_position
                or location_position_id.final_position != final_position
            ):
                location_position_id.write(
                    {
                        "initial_position": initial_position,
                        "final_position": final_position,
                    }
                )
        else:
            location_position_obj.create(
                {
                    "product_template_id": self.product_id.product_tmpl_id.id,
                    "stock_location_id": self.location_id.id,
                    "initial_position": initial_position or "",
                    "final_position": final_position or "",
                }
            )

        return res

    @api.model
    def create(self, vals):
        rec = super(StockQuant, self).create(vals)

        for record in rec:
            location_position_id = self.env["stock.location.position"].search(
                [
                    "&",
                    ("product_template_id", "=", record.product_id.product_tmpl_id.id),
                    ("stock_location_id", "=", record.location_id),
                ]
            )

            if location_position_id:
                vals["initial_position"] = location_position_id.initial_position
                vals["final_position"] = location_position_id.final_position

        return rec
