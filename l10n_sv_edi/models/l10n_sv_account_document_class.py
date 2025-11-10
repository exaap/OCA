# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class L10nSvAccountDocumentClass(models.Model):
    _inherit = "l10n_sv_account.document.class"

    generation_type = fields.Selection(
        selection=[("1", "Physical"), ("2", "Electronic")],
        string="Generation Type",
        default=False,
    )
