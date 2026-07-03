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

    @api.model_create_multi
    def create(self, vals_list):
        product_set_obj = self.env["product.set"]
        records = self.env["product.template"]

        for vals in vals_list:
            set_line_ids = vals.pop("set_line_ids", False)
            record = super(ProductTemplate, self).create(vals)
            records |= record

            if set_line_ids:
                values = {
                    "product_template_id": record.id,
                    "is_kit": True,
                    "ref": record.default_code,
                    "name": record.name,
                    "set_line_ids": set_line_ids,
                }
                product_set_obj.create(values)

        return records

    def write(self, vals):
        if "set_line_ids" in vals:
            product_set_obj = self.env["product.set"]
            set_line_ids = vals.pop("set_line_ids", False)

            for record in self:
                product_set_id = product_set_obj.search(
                    [("product_template_id", "=", record.id)], limit=1
                )

                if not product_set_id:
                    values = {
                        "product_template_id": record.id,
                        "is_kit": True,
                        "ref": record.default_code,
                        "name": record.name,
                    }
                    product_set_id = product_set_obj.create(values)

                product_set_id.write({"set_line_ids": set_line_ids})

        return super(ProductTemplate, self).write(vals)
