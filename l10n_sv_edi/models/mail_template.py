# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from base64 import b64encode
from odoo import models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def generate_email(self, res_ids, fields):
        res = super(MailTemplate, self).generate_email(res_ids, fields)
        multi_mode = True

        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        if self.model != "account.move":
            return res

        for move_id in self.env[self.model].browse(res_ids):
            if not move_id.dte_stamp_received or move_id.dte_sent_by_email:
                continue

            mail_values = res[move_id.id] if multi_mode else res
            invoice_report_id = move_id.company_id.l10n_sv_invoice_report_id
            pdf_name = "%s.pdf" % (move_id.dte_control_number.replace("/", "_"))
            pdf_content = invoice_report_id._render_qweb_pdf(
                invoice_report_id.report_name, [move_id.id]
            )
            pdf_attachment_ids = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", "account.move"),
                    ("res_id", "in", [move_id.id]),
                    ("name", "in", [move_id.name.replace("/", "_") + ".pdf", pdf_name]),
                ]
            )
            pdf_attachment_ids.unlink()
            pdf_attachment_id = self.env["ir.attachment"].create(
                {
                    "name": pdf_name,
                    "type": "binary",
                    "datas": b64encode(pdf_content[0]),
                    "res_model": "account.move",
                    "res_id": move_id.id,
                    "mimetype": "application/x-pdf",
                }
            )
            json_attachment_id = move_id.action_set_dte_json()
            mail_values["attachment_ids"] = [
                pdf_attachment_id.id,
                json_attachment_id.id,
            ]

        return res
