# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    country_code = fields.Char(related="country_id.code", store=False)
