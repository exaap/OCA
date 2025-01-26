# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class L10nSvAccountDocumentClass(models.Model):
    _name = "l10n_sv_account.document.class"
    _description = "Document Classes"

    code = fields.Char(string="Code")
    name = fields.Char(string="Name")
