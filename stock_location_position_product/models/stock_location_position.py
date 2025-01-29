# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api, _


class StockLocationPosition(models.Model):
    _name = "stock.location.position"
    _description = "Stock Location Positions"

    stock_location_id = fields.Many2one(
        string="Stock Location", comodel_name="stock.location", required=True
    )
    product_template_id = fields.Many2one(
        string="Product Template", comodel_name="product.template", required=True
    )
    initial_position = fields.Char(string="Initial Position", required=True)
    final_position = fields.Char(string="Final Position", required=True)

    _sql_constraints = [
        (
            "stock_location_product_template_unique",
            "UNIQUE(stock_location_id, product_template_id)",
            _("The combination of stock location and product must be unique!"),
        )
    ]

    def name_get(self):
        res = []

        for record in self:
            name = "[%s: %s ---> %s]" % (
                record.stock_location_id.display_name or "",
                record.initial_position or "",
                record.final_position or "",
            )
            res.append((record.id, name))

        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []

        if name:
            args = [
                "|",
                "|",
                ("stock_location_id", operator, name),
                ("initial_position", operator, name),
                ("final_position", operator, name),
            ] + args

        return self.search(args, limit=limit).name_get()
