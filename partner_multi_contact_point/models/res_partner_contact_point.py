# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models

CONTACT_POINT_TYPES = [("phone", "Phone"), ("mobile", "Mobile"), ("email", "Email")]


class ResPartnerContactPoint(models.Model):
    _name = "res.partner.contact.point"
    _description = "Contact Points"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    type = fields.Selection(
        selection=CONTACT_POINT_TYPES, string="Type", required=True, default="phone"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Contact", required=True, ondelete="cascade"
    )
    phone_extension = fields.Char(
        string="Phone Extension", help="Phone Number Extension."
    )
    contact_name = fields.Char()
    job_position_id = fields.Many2one(
        comodel_name="res.partner.job_position", string="Categorized job position"
    )

    def name_get(self):
        res = []

        for record in self:
            name = "%s" % (record.name or "")
            res.append((record.id, name))

        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []

        if name:
            state = self.search([("name", operator, name)] + args, limit=limit)
        else:
            state = self.search([], limit=limit)

        return state.name_get()

    def check_contact_points(self):
        for cp_id in self:
            if "," in cp_id.name:
                for i, cp_name in enumerate([n.strip() for n in cp_id.name.split(",")]):
                    if i == 0:
                        cp_id.with_context(no_edit=True).write({"name": cp_name})
                    else:
                        cp_copy_id = self.with_context(no_edit=True).create(
                            {
                                "name": cp_id.name,
                                "type": cp_id.type,
                                "partner_id": cp_id.partner_id.id,
                                "phone_extension": cp_id.phone_extension,
                                "contact_name": cp_id.contact_name,
                                "job_position_id": cp_id.job_position_id.id or False,
                            }
                        )
                        cp_copy_id.with_context(no_edit=True).write({"name": cp_name})

    def set_contact_points(self):
        cp_id = self.partner_id.contact_point_ids.filtered(
            lambda cp: cp.type == self.type
        )[:1]
        self.partner_id.write({self.type: cp_id.name})

        if self.type == "phone":
            self.partner_id.write(
                {
                    "phone_extension": cp_id.phone_extension,
                    "job_position_id": cp_id.job_position_id.id or False,
                }
            )

    @api.model
    def create(self, vals):
        rec = super(ResPartnerContactPoint, self).create(vals)

        if not self._context.get("no_edit"):
            rec.check_contact_points()

            for partner_id in rec.mapped("partner_id"):
                partner_id.set_contact_points(True)

        return rec

    def write(self, vals):
        res = super(ResPartnerContactPoint, self).write(vals)

        if not self._context.get("no_edit"):
            self.check_contact_points()
            self.set_contact_points()

        return res

    def unlink(self):
        partner_ids = self.mapped("partner_id")
        res = super(ResPartnerContactPoint, self).unlink()

        for partner_id in partner_ids:
            partner_id.set_contact_points()

        return res
