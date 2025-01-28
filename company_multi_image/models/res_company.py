# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_image_ids = fields.One2many(
        string='Company Images',
        comodel_name='res.company.image',
        inverse_name='company_id')
