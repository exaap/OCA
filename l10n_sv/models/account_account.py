# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    l10n_sv_is_internal_exempt_purchase = fields.Boolean(
        string="Internal Exempt Purchase?"
    )
    l10n_sv_is_internal_vat_tax = fields.Boolean(string="Internal VAT Tax?")
    l10n_sv_is_external_vat_tax = fields.Boolean(string="External VAT Tax?")
    l10n_sv_is_fovial_tax = fields.Boolean(string="FOVIAL Tax?")
