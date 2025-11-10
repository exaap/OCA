# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class L10nLatamIdentificationType(models.Model):
    _inherit = "l10n_latam.identification.type"

    l10n_sv_document_code = fields.Char("Document Code")

    def name_get(self):
        res = []

        for record in self:
            name = "[%s] %s" % (record.l10n_sv_document_code, record.name)
            res.append((record.id, name))

        return res
