# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_required_application = fields.Boolean(
        string="Required Application?", default=True
    )
