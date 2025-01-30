# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    location_position = fields.Char(
        string="Computed Stock Location Positions", compute="_compute_location_position"
    )
    location_position_ids = fields.One2many(
        string="Stock Location Positions",
        comodel_name="stock.location.position",
        inverse_name="product_template_id",
    )

    @api.depends("location_position_ids")
    def _compute_location_position(self):
        for record in self:
            location_position = ""

            for location_position_id in record.location_position_ids:
                if location_position == "":
                    location_position = location_position_id.display_name
                else:
                    location_position += ", " + location_position_id.display_name

            record.location_position = location_position
