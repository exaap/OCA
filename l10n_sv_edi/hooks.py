# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    update_existing_account_journal(env)


def update_existing_account_journal(env):
    journal_ids = env["account.journal"].search([("type", "in", ("sale", "purchase"))])

    for journal_id in journal_ids:
        journal_id.write({"debitnote_sequence": True})

    return
