# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    company_type = fields.Selection(
        selection=[("person", "Natural Person"), ("company", "Juridical Person")]
    )
    industry_id = fields.Many2one(domain="[('type', '!=', 'view')]")
    secondary_industry_ids = fields.Many2many(
        domain="[('id', '!=', industry_id), ('type', '!=', 'view')]"
    )
    l10n_latam_identification_type_id = fields.Many2one(default=False)
    taxpayer_registration_number = fields.Char(
        string="Taxpayer Registration Number",
        compute=lambda s: s._compute_identification(
            "taxpayer_registration_number", "nrc"
        ),
        inverse=lambda s: s._inverse_identification(
            "taxpayer_registration_number", "nrc"
        ),
        search=lambda s, *a: s._search_identification("nrc", *a),
    )

    @api.onchange("country_id")
    def _onchange_country(self):
        if self.country_id and self.company_type == "company":
            super(ResPartner, self)._onchange_country()

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []

        if name:
            args = [
                "|",
                "|",
                ("display_name", operator, name),
                ("vat", operator, name),
                ("email", operator, name),
            ] + args

        return self.search(args, limit=limit).name_get()
