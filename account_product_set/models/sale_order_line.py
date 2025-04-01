# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_set_sale_id = fields.Many2one(
        comodel_name="product.set.sale", string="Kit", readonly=True
    )

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)

        if res:
            res.update({"product_set_sale_id": self.product_set_sale_id.id})

        return res
