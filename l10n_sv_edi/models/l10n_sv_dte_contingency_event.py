# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from datetime import datetime
from pytz import timezone
from uuid import uuid4
from odoo import fields, models, _


class L10nSvDteContingencyEvent(models.Model):
    _name = "l10n_sv_dte.contingency.event"
    _description = "DTE Contingency Events"

    def _default_sales_point_id(self):
        sales_point_id = self.env["res.sales.point"].search([], limit=2)

        return sales_point_id.id if len(sales_point_id) == 1 else False

    sales_point_id = fields.Many2one(
        comodel_name="res.sales.point",
        string="Sales Point",
        default=_default_sales_point_id,
    )
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", copy=False
    )
    generation_code = fields.Char(string="Generation Code", readonly=True, copy=False)
    type = fields.Selection(
        selection=[
            ("1", "MH system unavailability"),
            ("2", "Issuer system unavailability"),
            ("3", "Failure in the Issuer's internet service supply"),
            (
                "4",
                "Failure in the supply of electrical energy service of the Issuer that prevents the transmission of the DTE",
            ),
            (
                "5",
                "Other (you must enter a maximum of 500 characters explaining the reason)",
            ),
        ],
        string="Type",
        default=False,
        copy=False,
    )
    reason = fields.Char(string="Reason", size=500, copy=False)
    start_date = fields.Date(string="Start Date", required=True, copy=False)
    end_date = fields.Date(string="End Date", required=True, copy=False)
    stamp_received = fields.Char(string="Stamp Received", readonly=True, copy=False)
    response_contingencia = fields.Text(
        string="Response contingencia(POST)", readonly=True, copy=False
    )

    def name_get(self):
        res = []

        for record in self:
            name = record.stamp_received if record.stamp_received else _("Unsent")
            name = "%s->%s (%s)" % (record.start_date, record.end_date, name)
            res.append((record.id, name))

        return res

    def _get_section_identificacion(self):
        if not self.generation_code:
            self.generation_code = str(uuid4()).upper()

        issue_time = datetime.now(timezone("America/El_Salvador"))

        return {
            "version": 3,
            "ambiente": self.company_id.l10n_sv_destination_environment,
            "codigoGeneracion": self.generation_code,
            "fTransmision": str(fields.Date.today()),
            "hTransmision": issue_time.strftime("%H:%M:%S"),
        }

    def _get_section_emisor(self):
        values = self.company_id.partner_id._get_partner_values("issuer")
        values["nombreResponsable"] = self.env.user.partner_id.name
        values["tipoDocResponsable"] = (
            self.env.user.partner_id.l10n_latam_identification_type_id.l10n_sv_document_code
            or "13"
        )
        values["numeroDocResponsable"] = self.env.user.partner_id._get_partner_vat()
        values["tipoEstablecimiento"] = self.sales_point_id.branch_id.type
        values["codEstableMH"] = None
        values["codPuntoVenta"] = self.sales_point_id.code

        return values

    def _get_section_detalleDTE(self):
        dte_contingency_ids = self.env["account.move"].search(
            [("dte_contingency_event_id", "=", self.id)]
        )
        values = []
        num_item = 1

        for dte_contingency_id in dte_contingency_ids:
            values.append(
                {
                    "noItem": num_item,
                    "tipoDoc": dte_contingency_id.dte_document_type_id.code,
                    "codigoGeneracion": dte_contingency_id.dte_generation_code,
                }
            )
            num_item += 1

        return values

    def _get_section_motivo(self):
        return {
            "fInicio": str(self.start_date),
            "fFin": str(self.end_date),
            "hInicio": "08:00:00",
            "hFin": "20:00:00",
            "tipoContingencia": int(self.type),
            "motivoContingencia": self.reason or None,
        }

    def _get_signed_json(self):
        unsigned_json = {"identificacion": self._get_section_identificacion()}
        unsigned_json["emisor"] = self._get_section_emisor()
        unsigned_json["detalleDTE"] = self._get_section_detalleDTE()
        unsigned_json["motivo"] = self._get_section_motivo()

        return self.company_id.action_post_signer(unsigned_json)

    def action_post_contingencia(self):
        reponse_contingencia = self.company_id._execute_api_request(
            "fesv/contingencia",
            {
                "nit": self.company_id.partner_id._get_partner_vat(),
                "documento": self._get_signed_json(),
            },
        )
        stamp_received = reponse_contingencia.get("selloRecibido")
        self.write(
            {
                "stamp_received": stamp_received,
                "response_contingencia": reponse_contingencia,
            }
        )
