# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    name = fields.Char(string="Name", translate=False)
    l10n_sv_edi = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")],
        string="E-Invoicing Tax?",
        default=False,
    )
    l10n_sv_code = fields.Char(string="E-Invoicing Code")
    l10n_sv_type = fields.Selection(
        selection=[("tax", "Tax"), ("withholding_tax", "Withholding Tax")],
        string="Type",
        default=False,
    )
