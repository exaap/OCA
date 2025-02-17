# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ResCityZipDistrict(models.Model):
    _name = "res.city.zip.district"
    _description = "Districts"

    name = fields.Char(string="District", required=True)
    zip_id = fields.Many2one(
        comodel_name="res.city.zip", string="ZIP Location", required=True
    )

    _sql_constraints = [
        (
            "name_zip_unique",
            "UNIQUE(name, zip_id)",
            "You already have a district with that name in the same zip. "
            "The district must be unique within it's zip.",
        )
    ]

    def name_get(self):
        res = []

        for record in self:
            if record.zip_id:
                name = "%s [%s, %s]" % (
                    record.name or "",
                    record.zip_id.name or "",
                    record.zip_id.city_id.name or "",
                )
            else:
                name = "%s" % (record.name or "")

            res.append((record.id, name))

        return res
