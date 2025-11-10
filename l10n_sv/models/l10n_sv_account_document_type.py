# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class L10nSvAccountDocumentType(models.Model):
    _name = "l10n_sv_account.document.type"
    _description = "Document Types"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
