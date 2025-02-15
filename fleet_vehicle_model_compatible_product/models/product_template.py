# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fleet_vehicle_model_ids = fields.Many2many(
        comodel_name="fleet.vehicle.model",
        relation="product_template_fleet_vehicle_model_rel",
        column1="product_template_id",
        column2="fleet_vehicle_model_id",
        string="Compatible Vehicle Models",
    )
