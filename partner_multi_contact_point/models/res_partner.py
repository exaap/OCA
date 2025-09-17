# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models

from .res_partner_contact_point import CONTACT_POINT_TYPES


class ResPartner(models.Model):
    _inherit = "res.partner"

    contact_point_ids = fields.One2many(
        comodel_name="res.partner.contact.point",
        inverse_name="partner_id",
        string="Contact Points",
    )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        res = super(ResPartner, self).name_search(name, args, operator, limit)

        if name:
            args = [
                "|",
                ("contact_point_ids", operator, name),
                ("id", "in", [x[0] for x in res]),
            ]

            return self.search(args, limit=limit).name_get()

        return res

    def set_contact_points(self, cp_create=False):
        for cp_type, cp_label in CONTACT_POINT_TYPES:
            cp_name = self.mapped(cp_type)[0]
            cp_id = self.contact_point_ids.filtered(
                lambda cp: cp.type == cp_type and cp.name == cp_name
            )

            if cp_name and not cp_id and cp_create:
                cp_id = self.contact_point_ids.with_context(no_edit=True).create(
                    {"name": cp_name, "partner_id": self.id, "type": cp_type}
                )

                if cp_type == "phone":
                    cp_id.with_context(no_edit=True).write(
                        {
                            "phone_extension": self.phone_extension,
                            "job_position_id": self.job_position_id.id or False,
                        }
                    )

            cp_id = self.contact_point_ids.filtered(lambda cp: cp.type == cp_type)[:1]
            self.write({cp_type: cp_id.name})

            if cp_type == "phone":
                self.write(
                    {
                        "phone_extension": cp_id.phone_extension,
                        "contact_name": cp_id.contact_name,
                        "job_position_id": cp_id.job_position_id.id or False,
                    }
                )
