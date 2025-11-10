# Copyright 2021 Akretion France (http://www.akretion.com/)
# Copyright 2022 Vauxoo (https://www.vauxoo.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# @author: Moisés López <moylop260@vauxoo.com>
# @author: Francisco Luna <fluna@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    update_existing_res_partner_industry(env)


def update_existing_res_partner_industry(env):
    industry_ids = env["res.partner.industry"].search([("parent_id", "=", False)])

    for industry_id in industry_ids:
        industry_id.write({"type": "view"})

    return
