# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    set_line_ids = fields.One2many(
        comodel_name="product.set.line",
        inverse_name="product_template_id",
        string="Products",
    )
