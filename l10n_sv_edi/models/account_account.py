# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    l10n_sv_unsent_account = fields.Boolean(string="Unsent Account?")
