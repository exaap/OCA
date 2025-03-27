# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, api


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.multi
    def post_inventory(self):
        res = super(StockInventory, self).post_inventory()

        for line_id in self.line_ids:
            line_id.product_id.last_inventory_date = self.date

        return res
