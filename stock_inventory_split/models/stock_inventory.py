# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    split_missing = fields.Boolean(String="Split Missing?")
    split_surpluses = fields.Boolean(String="Split Surpluses?")
