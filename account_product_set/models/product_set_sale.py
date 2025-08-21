# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models, api


class ProductSetSale(models.Model):
    _name = "product.set.sale"
    _description = "Product Sets of the Sale"

    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Kit",
        domain=[("set_line_ids", "!=", False)],
        required=True,
    )
    product_qty = fields.Float(string="Quantity", default=0)
    price_unit = fields.Float(string="Price Unit")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            rec.price_unit = rec.product_id.lst_price

    def name_get(self):
        res = []

        for record in self:
            name = "[%s] %s" % (
                record.product_id.default_code or "",
                record.product_id.name or "",
            )
            res.append((record.id, name))

        return res
