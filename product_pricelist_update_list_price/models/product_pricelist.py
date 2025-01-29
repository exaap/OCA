# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    update_list_price = fields.Boolean(string="Update Sales Price?")

    @api.model
    def create(self, vals):
        rec = super(ProductPricelist, self).create(vals)

        for product_priceliste_id in rec:
            if product_priceliste_id.update_list_price:
                product_priceliste_id.check_update_list_price()

        return rec

    @api.multi
    def write(self, vals):
        res = super(ProductPricelist, self).write(vals)

        for product_priceliste_id in self:
            if product_priceliste_id.update_list_price:
                product_priceliste_id.check_update_list_price()

        return res

    def check_update_list_price(self):
        msg = _(
            "The 'Update Sales Price?' field cannot be marked on more than one pricelist."
        )
        product_priceliste_ids = self.env["product.pricelist"].search(
            [("id", "!=", self.id), ("update_list_price", "=", True)]
        )

        if len(product_priceliste_ids) > 0:
            raise ValidationError(msg)

        return True
