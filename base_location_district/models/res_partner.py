# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    district_id = fields.Many2one(
        comodel_name="res.city.zip.district", string="District"
    )

    @api.onchange("district_id")
    def _onchange_district_id(self):
        if self.district_id:
            self.zip_id = self.district_id.zip_id
