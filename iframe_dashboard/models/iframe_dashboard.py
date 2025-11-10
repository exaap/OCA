# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api
from odoo.addons.board.controllers.main import Board


class iFrameDashboard(models.Model):
    _name = "iframe.dashboard"
    _description = "iFrames Dashboards"

    name = fields.Char(required=True)
    url = fields.Char(string="URL", required=True)
    width = fields.Integer(string="Width(%)", default=500)
    height = fields.Integer(string="Height(px)", default=700)
    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="iframe_dashboard_res_users_rel",
        column1="user_id",
        column2="iframe_dashboard_id",
        string="Owners",
    )

    """
    @api.model_create_multi
    def create(self, vals_list):
        records = super(iFrameDashboard, self).create(vals_list)
        action_id = self.sudo().env.ref("iframe_dashboard.iframe_dashboard_action")
        board = Board()

        for record in records:
            context_to_save = {
                "lang": record.create_uid._context["lang"],
                "tz": record.create_uid._context["tz"],
                "uid": record.create_uid._context["uid"],
                "group_by": [],
                "orderedBy": [],
                "dashboard_merge_domains_contexts": False,
            }
            board.add_to_dashboard(
                action_id=action_id.id,
                context_to_save=context_to_save,
                domain=[("id", "=", record.id)],
                view_mode="kanban",
                name=vals["name"],
            )

        return records
    """
