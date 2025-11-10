# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models, _


class ResPartnerIndustry(models.Model):
    _inherit = "res.partner.industry"

    code = fields.Char(string="Code")
    name = fields.Char(string="Name", translate=False)
    parent_id = fields.Many2one(domain="[('type', '=', 'view')]")
    type = fields.Selection(
        selection=[("view", "View"), ("other", "Other")],
        string="Type",
        default="other",
        required=True,
    )

    _sql_constraints = [("code_unique", "UNIQUE(code)", _("The code must be unique!"))]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []

        if name:
            args = [
                "|",
                "|",
                ("code", operator, name),
                ("name", operator, name),
                ("full_name", operator, name),
            ] + args

        return self.search(args, limit=limit).name_get()

    def name_get(self):
        res = []

        for record in self:
            if record.code:
                name = "[%s] %s" % (record.code, record.name)
            else:
                name = record.name

            res.append((record.id, name))

        return res
