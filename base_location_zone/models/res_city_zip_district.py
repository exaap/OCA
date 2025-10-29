# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ResCityZipDistrict(models.Model):
    _inherit = "res.city.zip.district"

    zone_id = fields.Many2one(comodel_name="res.city.zip.zone", string="Zone")
