# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class ResBranch(models.Model):
    _inherit = "res.branch"

    code = fields.Char(string="Code", size=4, required=True)
    type = fields.Selection(
        selection=[
            ("01", "Branch"),
            ("02", "Head Office"),
            ("04", "Warehouse"),
            ("07", "Courtyard"),
        ],
        string="Type",
        default=False,
    )
    sales_point_ids = fields.One2many(
        comodel_name="res.sales.point", inverse_name="branch_id", string="Sales Points"
    )

    _sql_constraints = [
        (
            "code_unique",
            "unique(company_id, code)",
            "Branch code must be unique per company!",
        )
    ]
