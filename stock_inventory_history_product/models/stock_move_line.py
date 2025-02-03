# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    previous_inventory_quantity = fields.Float(
        string="Previous Inventory Quantity", digits="Product Unit of Measure"
    )
    counted_inventory_quantity = fields.Float(
        string="Counted Inventory Quantity", digits="Product Unit of Measure"
    )
