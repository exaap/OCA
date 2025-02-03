# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    date = fields.Datetime(related="inventory_id.date")
