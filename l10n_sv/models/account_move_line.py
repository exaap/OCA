# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_sv_account_document_id = fields.Many2one(
        comodel_name="l10n_sv_account.document", string="Document"
    )
