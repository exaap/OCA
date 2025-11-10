# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def unlink(self):
        for move_id in self:
            if move_id.journal_id.sequence_id and move_id.name not in [False, "/"]:
                raise UserError(
                    _(
                        """You cannot delete an journal entry after it has been validated"""
                        '''(and received a number). You can set it back to "Draft"'''
                        """state and modify its content, then re-confirm it."""
                    )
                )

        return super(AccountMove, self).unlink()

    def write(self, vals):
        if vals.get("journal_id") and not vals.get("name"):
            journal_id = module = self.env["account.journal"].search(
                [("id", "=", vals.get("journal_id"))]
            )

            for move_id in self:
                if (
                    move_id.name not in [False, "/"]
                    and move_id.state == "draft"
                    and move_id.journal_id.sequence_id
                    and journal_id.sequence_id
                    and move_id.journal_id.sequence_id.id == journal_id.sequence_id.id
                ):
                    vals.pop("journal_id")
                    move_id.write({"posted_before": False})
                    move_id.write({"journal_id": journal_id.id, "name": move_id.name})

        return super(AccountMove, self).write(vals)

    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        if not self.quick_edit_mode:
            self._compute_name_by_sequence()
