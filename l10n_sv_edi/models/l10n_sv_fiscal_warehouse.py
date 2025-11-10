# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class L10nSvFiscalWarehouse(models.Model):
    _name = "l10n_sv_fiscal.warehouse"
    _description = "Fiscal Warehouses"

    code = fields.Char(string="Code", size=2, required=True)
    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Fiscal Warehouse code must be unique!")
    ]
