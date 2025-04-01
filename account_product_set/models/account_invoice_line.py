# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    product_set_sale_id = fields.Many2one(
        comodel_name="product.set.sale", string="Kit", readonly=True
    )
