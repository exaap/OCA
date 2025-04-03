# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    product_set_sale_ids = fields.One2many(
        comodel_name="product.set.sale",
        inverse_name="sale_order_id",
        string="Product Sets of the Sale",
    )

    @api.multi
    def action_update_product_set_sale_ids(self):
        values = []

        for order_line_id in self.order_line:
            if order_line_id.product_id.set_line_ids:
                values.append(
                    (
                        0,
                        0,
                        {
                            "product_id": order_line_id.product_id.id,
                            "product_qty": order_line_id.product_uom_qty,
                            "price_unit": order_line_id.price_unit,
                            "discount": order_line_id.discount,
                        },
                    )
                )
                order_line_id.unlink()

            if order_line_id.product_set_sale_id:
                order_line_id.unlink()

        if values:
            self.write({"product_set_sale_ids": values})

        values = []

        for product_set_sale_id in self.product_set_sale_ids:
            for set_line_id in product_set_sale_id.product_id.set_line_ids:
                if product_set_sale_id.product_qty <= 0 and set_line_id.quantity <= 0:
                    raise UserError(_("Product quantity must be greater than zero."))

                price_unit = 0

                if set_line_id.percent_price > 0:
                    price_unit = product_set_sale_id.price_unit
                    percent_price = set_line_id.percent_price / 100
                    price_unit = price_unit * percent_price / set_line_id.quantity

                values.append(
                    (
                        0,
                        0,
                        {
                            "sequence": 100,
                            "product_id": set_line_id.product_id.id,
                            "product_uom_qty": product_set_sale_id.product_qty
                            * set_line_id.quantity,
                            "price_unit": price_unit,
                            "discount": set_line_id.discount,
                            "product_set_sale_id": product_set_sale_id.id,
                        },
                    )
                )

        self.write({"order_line": values})

    @api.multi
    def action_confirm(self):
        if any([l.product_id.set_line_ids for l in self.order_line]):
            self.action_update_product_set_sale_ids()

        return super(SaleOrder, self).action_confirm()
