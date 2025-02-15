# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).


from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_open_account_move_line(self):
        line_obj = self.env["account.move.line"]
        lines = line_obj.search([("stock_move_id", "in", self.move_lines.ids)])

        if lines:
            xml_id = "account.action_account_moves_all_a"
            action = self.env.ref(xml_id).read()[0]
            ids = set([x.id for x in lines])
            action["domain"] = "[('id', 'in', %s)]" % list(ids)

            return action
