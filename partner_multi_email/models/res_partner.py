# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    email_ids = fields.One2many(
        comodel_name="res.partner.email", inverse_name="partner_id", string="Emails"
    )
    email = fields.Char(
        string="Main Email",
        compute="_compute_email",
        store=True,
        inverse="_inverse_email",
        compute_sudo=True,
        inverse_sudo=True,
    )

    @api.depends("email_ids.name", "email_ids.sequence")
    def _compute_email(self):
        for partner_id in self:
            partner_id.email = partner_id.email_ids[:1].name

    def _inverse_email(self):
        for partner_id in self:
            if partner_id.email_ids:
                partner_id.email_ids[:1].write({"name": partner_id.email})
            elif not partner_id.email:
                partner_id.email_ids.unlink()
            else:
                self.env["res.partner.email"].create(self._prepare_email_vals())

    def _prepare_email_vals(self):
        self.ensure_one()

        return {"partner_id": self.id, "name": self.email}

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        res = super(ResPartner, self).name_search(name, args, operator, limit)

        if name:
            args = [
                "|",
                ("email_ids", operator, name),
                ("id", "in", [x[0] for x in res]),
            ]

            return self.search(args, limit=limit).name_get()

        return res
