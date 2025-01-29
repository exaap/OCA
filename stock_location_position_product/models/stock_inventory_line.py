# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    initial_position = fields.Char(string="Initial Position")
    final_position = fields.Char(string="Final Position")

    @api.multi
    def write(self, vals):
        if vals.get("initial_position") or vals.get("final_position"):
            location_position_obj = self.env["stock.location.position"]
            location_position_id = location_position_obj.search(
                [
                    "&",
                    ("product_template_id", "=", self.product_id.product_tmpl_id.id),
                    ("stock_location_id", "=", self.location_id.id),
                ]
            )

            if location_position_id:
                location_position_id.write(
                    {
                        "initial_position": vals.get("initial_position")
                        or location_position_id.initial_position,
                        "final_position": vals.get("final_position")
                        or location_position_id.final_position,
                    }
                )
            else:
                location_position_obj.create(
                    {
                        "product_template_id": self.product_id.product_tmpl_id.id,
                        "stock_location_id": self.location_id.id,
                        "initial_position": vals.get("initial_position") or "",
                        "final_position": vals.get("final_position") or "",
                    }
                )

        return super(StockInventoryLine, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get("product_id"):
            product_id = self.env["product.product"].search(
                [("id", "=", vals.get("product_id"))]
            )
            location_position_id = self.env["stock.location.position"].search(
                [
                    "&",
                    ("product_template_id", "=", product_id.product_tmpl_id.id),
                    ("stock_location_id", "=", vals.get("location_id")),
                ]
            )

            if location_position_id:
                vals["initial_position"] = location_position_id.initial_position
                vals["final_position"] = location_position_id.final_position

        return super(StockInventoryLine, self).create(vals)

    @api.onchange("product_id")
    def _onchange_product(self):
        res = super(StockInventoryLine, self)._onchange_product()

        if self.product_id:
            location_position_id = self.env["stock.location.position"].search(
                [
                    "&",
                    ("product_template_id", "=", self.product_id.product_tmpl_id.id),
                    ("stock_location_id", "=", self.location_id.id),
                ]
            )

            if location_position_id:
                self.initial_position = location_position_id.initial_position
                self.final_position = location_position_id.final_position

        return res
