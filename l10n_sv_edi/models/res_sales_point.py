# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class ResSalesPoint(models.Model):
    _name = "res.sales.point"
    _description = "Company Sales Points"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    branch_id = fields.Many2one(
        comodel_name="res.branch", string="Branch", required=True
    )
    consecutive_count = fields.Json(string="Consecutive Count", default={})

    _sql_constraints = [
        (
            "code_unique",
            "unique(branch_id, code)",
            "Sales point code must be unique per branch!",
        )
    ]
