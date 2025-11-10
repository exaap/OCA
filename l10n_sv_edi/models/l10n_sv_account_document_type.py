# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class L10nSvAccountDocumentType(models.Model):
    _inherit = "l10n_sv_account.document.type"

    version = fields.Integer(string="Version", required=True, default=0)
    invoicing_model = fields.Selection(
        selection=[("1", "Prior"), ("2", "Deferred")],
        string="Invoicing Model",
        default=False,
    )
    transmission_type = fields.Selection(
        selection=[("1", "Normal"), ("2", "Contingency")],
        string="Transmission Type",
        default=False,
    )
