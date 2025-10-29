# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    zone_id = fields.Many2one(comodel_name="res.city.zip.zone", string="Zone")
    zone_group_id = fields.Many2one(
        comodel_name="res.city.zip.zone.groups", string="Zone Group"
    )

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        res = super(ResPartner, self)._onchange_zip_id()

        if self.zip_id:
            for zone_id in self.zip_id.zone_ids:
                self.zone_id = zone_id

                break

        return res

    @api.onchange("district_id")
    def _onchange_district_id(self):
        res = super(ResPartner, self)._onchange_district_id()

        if self.district_id:
            self.zone_id = self.district_id.zone_id

        return res

    @api.onchange("zone_id")
    def _onchange_zone_id(self):
        if self.zone_id:
            zone_group_id = self.env["res.city.zip.zone.groups"].search(
                [("zone_ids", "in", self.zone_id.ids)], limit=1
            )
            self.zone_group_id = zone_group_id
