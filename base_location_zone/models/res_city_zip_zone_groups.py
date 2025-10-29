# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ResCityZipZoneGroups(models.Model):
    _name = "res.city.zip.zone.groups"
    _description = "Zone Groups"

    name = fields.Char(size=64, required=True)
    zone_ids = fields.Many2many(
        comodel_name="res.city.zip.zone", string="Zones", ondelete="cascade"
    )
