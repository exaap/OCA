# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    taxpayer_registration_number = fields.Char(
        string="Taxpayer Registration Number",
        compute=lambda s: s._compute_identification(
            "taxpayer_registration_number", "nrc"
        ),
        inverse=lambda s: s._inverse_identification(
            "taxpayer_registration_number", "nrc"
        ),
        search=lambda s, *a: s._search_identification("nrc", *a),
    )
