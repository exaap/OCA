# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    product_template_id = fields.Many2one(related="product_set_id.product_template_id")
    percent_price = fields.Float(
        string="Percentage Price (%)",
        help="Percentage from 0 to 100 regarding the price of the Kit.",
        default=0.00,
    )
