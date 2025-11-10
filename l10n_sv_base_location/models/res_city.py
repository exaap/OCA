# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ResCity(models.Model):
    _inherit = "res.city"

    code = fields.Char(string="Code", size=2)
    name = fields.Char(string="Name", translate=False)
