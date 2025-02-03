# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    inventory_line_ids = fields.One2many(
        comodel_name="stock.inventory.line",
        inverse_name="product_id",
        string="Inventory Lines",
    )
    last_inventory_date = fields.Datetime(string="Last Inventory Date")
