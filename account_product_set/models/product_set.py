# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class ProductSet(models.Model):
    _inherit = "product.set"

    is_kit = fields.Boolean(string="Is Kit?")
    product_template_id = fields.Many2one(
        comodel_name="product.template", string="Product"
    )

    @api.onchange("is_kit")
    def _onchange_is_kit(self):
        if not self.is_kit:
            self.product_template_id = False

    @api.onchange("product_template_id")
    def _onchange_product_template_id(self):
        if self.product_template_id:
            self.ref = self.product_template_id.default_code
            self.name = self.product_template_id.name
