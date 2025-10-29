# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class ResCityZipZone(models.Model):
    _name = "res.city.zip.zone"
    _description = "Zones"

    name = fields.Char(size=64, required=True)
    district_ids = fields.Many2many(
        comodel_name="res.city.zip.district", string="Districts", ondelete="cascade"
    )
    zip_id = fields.Many2one(comodel_name="res.city.zip", string="ZIP Location")

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        districts_ids = self.env["res.city.zip.district"].search(
            [("zip_id", "=", self.zip_id.id)]
        )
        list_districts = [int(row) for row in districts_ids]
        self.update({"district_ids": [[6, 0, list_districts]]})
