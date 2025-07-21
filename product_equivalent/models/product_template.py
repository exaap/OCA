# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_equivalent_group_id = fields.Many2one(
        comodel_name="product.equivalent.group", string="Group of Equivalent Products"
    )
    product_equivalent_ids = fields.Many2many(
        related="product_equivalent_group_id.product_equivalent_ids"
    )
    old_product_equivalent_ids = fields.Many2many(
        comodel_name="product.equivalent",
        relation="product_template_product_equivalent_rel",
        column1="product_template_id",
        column2="product_equivalent_id",
        string="Old Equivalent Products",
    )

    @api.onchange("product_brand_id")
    def _onchange_product_brand_id(self):
        for record in self:
            if record.product_brand_id.partner_id:
                record.manufacturer = record.product_brand_id.partner_id
