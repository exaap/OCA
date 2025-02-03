# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def post_inventory(self):
        res = super(StockInventory, self).post_inventory()

        for move_id in self.move_ids:
            move_id.product_id.last_inventory_date = move_id.date

        return res
