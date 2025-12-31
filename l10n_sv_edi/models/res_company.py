# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from json import JSONDecodeError
from requests import get, post, exceptions

from odoo import fields, models, _
from odoo.exceptions import UserError

API_URL = "https://api%s.dtes.mh.gob.sv/%s"
MSG_ERROR = _("Error,\n\nStatus Code: %s,\nReason: %s\n\nContact your administrator.")


def execute_requests_method(url, headers, data=None, json=None, method=None):
    timeout = 10

    for attempt in range(3):
        try:
            response = (get if method == "GET" else post)(
                url, headers=headers, data=data, json=json, timeout=timeout
            )

            """if url != "https://apitest.dtes.mh.gob.sv/seguridad/auth":
                raise Warning(
                    response.status_code,
                    response.reason,
                    response.text,
                )"""

            if response.status_code in [200, 202, 400]:
                return response.json()

            raise UserError(_(MSG_ERROR) % (response.status_code, response.reason))
        except JSONDecodeError:
            raise UserError(_("Response is not valid JSON."))
        except exceptions.Timeout:
            if attempt < 2:
                timeout += 10

                continue

            raise UserError(_("Service generates a timeout error."))
        except exceptions.RequestException as e:
            raise UserError(
                _("Unknown Error,\n\n%s\n\nContact your administrator.") % e
            )


def show_error(response_json, code, message):
    raise UserError(
        _(MSG_ERROR)
        % (
            response_json.get(code, "N/A"),
            response_json.get(message, _("Unknown error.")),
        )
    )


class ResCompany(models.Model):
    _inherit = "res.company"

    def _default_l10n_sv_invoice_report_id(self):
        return self.env.ref("account.account_invoices")

    l10n_sv_edi_enabled = fields.Boolean(string="EDI Enabled?")
    l10n_sv_automatic_dte_sending = fields.Boolean(string="Automatic DTE sending?")
    l10n_sv_automatic_email_sending = fields.Boolean(string="Automatic email sending?")
    l10n_sv_dte_error_email = fields.Char(string="DTE Error Email")
    l10n_sv_invoice_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Invoice Report",
        required=True,
        domain="[('model', '=', 'account.move')]",
        default=_default_l10n_sv_invoice_report_id,
    )
    l10n_sv_destination_environment = fields.Selection(
        selection=[("00", "Test mode"), ("01", "Production mode")],
        string="Destination Environment",
    )
    l10n_sv_signer_url = fields.Char(
        string="Signer URL", default="http://localhost:8113/firmardocumento/"
    )
    l10n_sv_certificate_password = fields.Char(string="Certificate Password")
    l10n_sv_api_password = fields.Char(string="API Password")
    l10n_sv_api_token_date = fields.Datetime(string="API Token Date", readonly=True)
    l10n_sv_api_token = fields.Text(string="API Token", readonly=True)
    l10n_sv_dte_01_move_id = fields.Many2one(
        comodel_name="account.move",
        string="DTE Type 01",
        domain="[('dte_document_type_id.code', '=', '01'), ('dte_state', '=', 'dte_transmitted')]",
    )
    l10n_sv_dte_03_move_id = fields.Many2one(
        comodel_name="account.move",
        string="DTE Type 03",
        domain="[('dte_document_type_id.code', '=', '03'), ('dte_state', '=', 'dte_transmitted')]",
    )
    l10n_sv_dte_05_move_id = fields.Many2one(
        comodel_name="account.move",
        string="DTE Type 05",
        domain="[('dte_document_type_id.code', '=', '05'), ('dte_state', '=', 'dte_transmitted')]",
    )
    l10n_sv_dte_11_move_id = fields.Many2one(
        comodel_name="account.move",
        string="DTE Type 11",
        domain="[('dte_document_type_id.code', '=', '11'), ('dte_state', '=', 'dte_transmitted')]",
    )
    l10n_sv_dte_14_move_id = fields.Many2one(
        comodel_name="account.move",
        string="DTE Type 14",
        domain="[('dte_document_type_id.code', '=', '14'), ('dte_state', '=', 'dte_transmitted')]",
    )

    def action_post_signer(self, dte_json=None):
        response_json = execute_requests_method(
            self.l10n_sv_signer_url,
            {"Content-Type": "application/json;charset=UTF-8"},
            json={
                "nit": (self.vat or "").replace(self.country_id.code or "", ""),
                "passwordPri": self.l10n_sv_certificate_password,
                "dteJson": dte_json or {},
            },
        )

        if response_json.get("status") == "OK" and dte_json:
            return response_json.get("body")
        elif response_json.get("status") == "OK":
            raise UserError(_("SUCCESS: Signer works correctly."))

        show_error(response_json.get("body", {}), "codigo", "mensaje")

    def action_post_auth(self):
        if self.l10n_sv_api_token and self.l10n_sv_api_token_date:
            delta = fields.Datetime.now() - self.l10n_sv_api_token_date

            if delta.total_seconds() < 86400:
                return self.l10n_sv_api_token

        test = "test" if self.l10n_sv_destination_environment == "00" else ""
        response_json = execute_requests_method(
            API_URL % (test, "seguridad/auth"),
            {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
            data={
                "user": (self.vat or "").replace(self.country_id.code or "", ""),
                "pwd": self.l10n_sv_api_password,
            },
        )

        if response_json.get("status") == "OK":
            self.sudo().l10n_sv_api_token = response_json.get("body").get("token")
            self.sudo().l10n_sv_api_token_date = fields.Datetime.now()

            return self.l10n_sv_api_token

        show_error(response_json.get("body", {}), "codigoMsg", "descripcionMsg")

    def _execute_api_request(self, endpoint, json=None, method=None):
        test = "test" if self.l10n_sv_destination_environment == "00" else ""
        url = API_URL % (test, endpoint)
        headers = {
            "Authorization": self.action_post_auth(),
            "Content-Type": "application/json;charset=UTF-8",
        }
        response_json = execute_requests_method(url, headers, json=json, method=method)

        if response_json.get("estado") in ["PROCESADO", "RECIBIDO", "RECHAZADO"]:
            return response_json

        show_error(response_json, "codigoMsg", "descripcionMsg")

    def action_run_dte_tests(self):
        for company_id in self:
            move_id = company_id.l10n_sv_dte_01_move_id
            dte_document_type = "01"
            tests_number = 90
            sales_point_id = move_id.sales_point_id if move_id else False
            consecutive_count = sales_point_id.consecutive_count or {}
            year = str((move_id.invoice_date or fields.Date.today()).year)
            year_count = consecutive_count.get(year) or {}
            consecutive = year_count.get(dte_document_type, 0)

            while tests_number > 0:
                if move_id and consecutive < tests_number:
                    move_id.dte_control_number = False
                    move_id.dte_generation_code = False
                    move_id.action_post_recepciondte()
                    consecutive += 1
                else:
                    if dte_document_type == "01":
                        move_id = company_id.l10n_sv_dte_03_move_id
                        dte_document_type = "03"
                        tests_number = 75
                    elif dte_document_type == "03":
                        move_id = company_id.l10n_sv_dte_05_move_id
                        dte_document_type = "05"
                        tests_number = 50
                    elif dte_document_type == "05":
                        move_id = company_id.l10n_sv_dte_11_move_id
                        dte_document_type = "11"
                        tests_number = 90
                    elif dte_document_type == "11":
                        move_id = company_id.l10n_sv_dte_14_move_id
                        dte_document_type = "14"
                        tests_number = 25
                    elif dte_document_type == "14":
                        tests_number = 0

                    sales_point_id = move_id.sales_point_id if move_id else False
                    consecutive_count = sales_point_id.consecutive_count or {}
                    year = str((move_id.invoice_date or fields.Date.today()).year)
                    year_count = consecutive_count.get(year) or {}
                    consecutive = year_count.get(dte_document_type, 0)

    # TODO
    def action_post_recepcionlote(self):
        return self.company_id._execute_api_request(
            "fesv/recepcionlote/",
            {
                "ambiente": self.company_id.l10n_sv_destination_environment,
                "idEnvio": str(uuid4()).upper(),
                "version": "",
                "nitEmisor": self.company_id.partner_id._get_partner_vat(),
                "documentos": [],
            },
        ).get("codigoLote")

    def action_get_consultadtelote(self):
        codigo_lote = str(uuid4()).upper()

        return self.company_id._execute_api_request(
            f"fesv/recepcion/consultadtelote/{codigo_lote}", method="GET"
        )
