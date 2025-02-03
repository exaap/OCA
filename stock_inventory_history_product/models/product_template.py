# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    inventory_line_ids = fields.One2many(
        related="product_variant_id.inventory_line_ids"
    )
    last_inventory_date = fields.Datetime(
        related="product_variant_id.last_inventory_date"
    )
