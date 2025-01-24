# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        relation="stock_picking_type_res_users_rel",
        column1="user_id",
        column2="picking_type_id",
        string="Allowed Picking Types",
    )
    location_restriction = fields.Boolean(string="Stock Locations Restriction?")
    location_cancel_ids = fields.Many2many(
        comodel_name="stock.location",
        relation="stock_location_cancel_res_users_rel",
        column1="user_id",
        column2="location_id",
        string="Allowed Cancel Stock Locations",
    )
    location_done_ids = fields.Many2many(
        comodel_name="stock.location",
        relation="stock_location_done_res_users_rel",
        column1="user_id",
        column2="location_id",
        string="Allowed Done Stock Locations",
    )
