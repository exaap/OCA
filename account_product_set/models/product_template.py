# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    set_line_ids = fields.One2many(
        comodel_name="product.set.line",
        inverse_name="product_template_id",
        string="Product set line",
    )

    @api.multi
    def write(self, vals):
        if "set_line_ids" in vals:
            product_set_obj = self.env["product.set"]

            for record in self:
                product_set_id = product_set_obj.search(
                    [("product_template_id", "=", record.id)]
                )

                if not product_set_id:
                    product_set_id = product_set_obj.create(
                        {
                            "product_template_id": record.id,
                            "is_kit": True,
                            "ref": record.default_code,
                            "name": record.name,
                        }
                    )

                product_set_id.write({"set_line_ids": vals.get("set_line_ids")})

            vals.pop("set_line_ids", None)

        return super(ProductTemplate, self).write(vals)
