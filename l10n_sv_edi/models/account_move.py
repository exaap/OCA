# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

import logging
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from json import dumps
from num2words import num2words
from pytz import timezone
from qrcode import QRCode
from uuid import uuid4
from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DOCUMENT_TYPES = [
    "01",  # Factura
    "03",  # Comprobante de crédito fiscal
    "04",  # Nota de remisión
    "05",  # Nota de crédito
    "06",  # Nota de débito
    "07",  # Comprobante de retención
    "08",  # Comprobante de liquidación
    "09",  # Documento contable de liquidación
    "11",  # Facturas de exportación
    "14",  # Facturas de sujeto excluido
    "15",  # Comprobante de donación
]
TAXES_SECTION2 = ["A8", "57", "90", "D4", "D5", "A6"]
TAXES_CAT006 = ["22", "C4", "C9"]
URL = "https://admin.factura.gob.sv/consultaPublica?ambiente=%s&codGen=%s&fechaEmi=%s"


class AccountMove(models.Model):
    _inherit = "account.move"

    def _default_sales_point_id(self):
        sales_point_id = self.env["res.sales.point"].search([], limit=2)

        return sales_point_id.id if len(sales_point_id) == 1 else False

    def _default_dte_generation_code(self):
        return str(uuid4()).upper()

    @api.onchange("dte_invalidation_type")
    def onchange_dte_invalidation_type(self):
        if self.dte_invalidation_type in ["2", False]:
            self.dte_invalidation_move_id = False

    def _get_name_invoice_report(self):
        self.ensure_one()

        if self.company_id.country_id.code == "SV":
            return "l10n_sv_edi.report_invoice_document"

        return super(AccountMove, self)._get_name_invoice_report()

    @api.depends("state", "journal_id", "date")
    def _compute_name_by_sequence(self):
        for move_id in self:
            if (
                move_id.state == "posted"
                and (not move_id.name or move_id.name == "/")
                and move_id.journal_id
                and move_id.journal_id.type in ("sale", "purchase")
                and move_id.debit_origin_id
                and move_id.journal_id.debitnote_sequence
                and move_id.journal_id.debitnote_sequence_id
            ):
                seq_id = move_id.journal_id.debitnote_sequence_id
                name = seq_id.with_context(ir_sequence_date=move_id.date).next_by_id()
                move_id.name = name

        super(AccountMove, self)._compute_name_by_sequence()

    def action_post(self):
        res = super(AccountMove, self).action_post()

        for move_id in self:
            if not move_id.company_id.l10n_sv_edi_enabled:
                continue

            if move_id.dte_state:
                continue

            dte_document_type_id = move_id.journal_id.dte_document_type_id
            document_ref = "l10n_sv.l10n_sv_account_document_"

            if (
                move_id.reversed_entry_id
                and move_id.move_type == "out_refund"
                and dte_document_type_id
                and dte_document_type_id.code == "03"
            ):
                dte_document_type_id = self.env.ref(document_ref + "type_05")
            elif (
                move_id.debit_origin_id
                and move_id.move_type == "out_invoice"
                and dte_document_type_id
                and dte_document_type_id.code == "03"
            ):
                dte_document_type_id = self.env.ref(document_ref + "type_06")
            elif move_id.move_type == "in_invoice" and not dte_document_type_id:
                for line_id in self.line_ids.filtered(
                    lambda l: l.display_type in ["tax"]
                ):
                    if line_id.tax_group_id.l10n_sv_code in TAXES_CAT006:
                        dte_document_type_id = self.env.ref(document_ref + "type_07")

                        break
            elif move_id.move_type not in ["out_invoice", "in_invoice"]:
                dte_document_type_id = False

            if (
                not dte_document_type_id
                or dte_document_type_id.code not in DOCUMENT_TYPES
            ):
                continue

            move_id.dte_document_type_id = dte_document_type_id
            move_id.dte_state = "dte_unsent"

            if move_id.company_id.l10n_sv_automatic_dte_sending:
                move_id.action_post_recepciondte()

        return res

    sales_point_id = fields.Many2one(
        comodel_name="res.sales.point",
        string="Sales Point",
        default=_default_sales_point_id,
    )
    fiscal_warehouse_id = fields.Many2one(
        comodel_name="l10n_sv_fiscal.warehouse", string="Fiscal Warehouse", copy=False
    )
    export_regime_id = fields.Many2one(
        comodel_name="l10n_sv_export.regime", string="Export Regime", copy=False
    )
    supplier_dte_document_type_id = fields.Many2one(
        comodel_name="l10n_sv_account.document.type",
        string="Supplier DTE document type",
        domain="[('transmission_type', '!=', False)]",
        copy=False,
    )
    dte_document_type_id = fields.Many2one(
        comodel_name="l10n_sv_account.document.type",
        string="DTE Document Type",
        domain="[('transmission_type', '!=', False)]",
        copy=False,
    )
    dte_state = fields.Selection(
        selection=[
            ("dte_unsent", "DTE Unsent"),
            ("dte_rejected", "DTE Rejected"),
            ("dte_transmitted", "DTE Transmitted"),
            ("dte_invalidation_rejected", "DTE Invalidation Rejected"),
            ("dte_invalidated", "DTE Invalidated"),
        ],
        string="DTE State",
        default=False,
        copy=False,
    )
    dte_sent_by_email = fields.Boolean(string="DTE sent by email?", copy=False)
    dte_control_number = fields.Char(
        string="DTE Control Number", readonly=True, copy=False
    )
    dte_generation_code = fields.Char(
        string="DTE Generation Code",
        readonly=True,
        copy=False,
        default=_default_dte_generation_code,
    )
    dte_stamp_received = fields.Char(
        string="DTE Stamp Received", readonly=True, copy=False
    )
    dte_issue_time = fields.Char(string="DTE Issue Time", copy=False)
    dte_url = fields.Char(string="DTE URL", readonly=True, copy=False)
    dte_contingency_event_id = fields.Many2one(
        comodel_name="l10n_sv_dte.contingency.event",
        string="DTE Contingency Event",
        copy=False,
    )
    response_recepciondte = fields.Text(
        string="Response recepciondte(POST)", readonly=True, copy=False
    )
    response_consultadte = fields.Text(
        string="Response consultadte(POST)", readonly=True, copy=False
    )
    dte_invalidation_type = fields.Selection(
        selection=[
            (
                "1",
                "Error in the information of the Electronic Tax Document to invalidate.",
            ),
            ("2", "Rescind of the operation performed."),
            ("3", "Other"),
        ],
        string="DTE Invalidation Type",
        default=False,
        copy=False,
    )
    dte_invalidation_reason = fields.Char(
        string="DTE Invalidation Reason", size=200, copy=False
    )
    dte_invalidation_move_id = fields.Many2one(
        comodel_name="account.move",
        string="DTE that replaces this DTE",
        domain="[('id', '!=', id),"
        "('dte_stamp_received', '!=', False),"
        "('dte_invalidation_stamp_received', '=', False)]",
        copy=False,
    )
    dte_invalidation_generation_code = fields.Char(
        string="DTE Invalidation Generation Code", readonly=True, copy=False
    )
    dte_invalidation_stamp_received = fields.Char(
        string="DTE Invalidation Stamp Received", readonly=True, copy=False
    )
    response_anulardte = fields.Text(
        string="Response anulardte(POST)", readonly=True, copy=False
    )

    _sql_constraints = [
        (
            "dte_generation_code_unique",
            "unique(dte_generation_code)",
            "Generation code must be unique per company!",
        )
    ]

    def _set_dte_url(self):
        self.dte_url = URL % (
            self.company_id.l10n_sv_destination_environment,
            self.dte_generation_code,
            self.invoice_date,
        )

    def _get_dte_qrcode(self):
        qr_code = QRCode(version=4, box_size=4, border=1)
        qr_code.add_data(self.dte_url)
        qr_code.make(fit=True)
        image = qr_code.make_image()
        buffer = BytesIO()
        image.save(buffer, format="PNG")

        return b64encode(buffer.getvalue())

    def _get_value_in_letters(self, total):
        integer = int(total)
        decimals = int(round(total - integer, 2) * 100)
        currency_name = self.currency_id.name
        currency_name = _("Dollar(s)") if currency_name == "USD" else currency_name
        value_in_letters = (
            num2words(integer, lang="es").capitalize() + " " + currency_name
        )

        if decimals > 0:
            value_in_letters += " con " + num2words(decimals, lang="es") + _(" Cent(s)")

        return value_in_letters

    def _get_dte_control_number(self, dte_document_type_id):
        if not self.dte_control_number and dte_document_type_id.version != 0:
            sales_point_id = self.sales_point_id
            consecutive_count = sales_point_id.consecutive_count or {}
            year = str((self.invoice_date or fields.Date.today()).year)
            year_count = consecutive_count.get(year) or {}
            consecutive = year_count.get(dte_document_type_id.code, 0) + 1
            year_count[dte_document_type_id.code] = consecutive
            consecutive_count[year] = year_count
            sales_point_id.consecutive_count = consecutive_count
            self.dte_control_number = (
                "DTE-"
                + dte_document_type_id.code
                + "-"
                + sales_point_id.branch_id.code
                + sales_point_id.code
                + "-"
                + str(consecutive).zfill(15)
            )

        return self.dte_control_number

    def _get_dte_generation_code(self):
        if not self.dte_generation_code:
            self.dte_generation_code = str(uuid4()).upper()

        self._set_dte_url()
        _logger.info("DTE Generation Code: %s", self.dte_generation_code)

        return self.dte_generation_code

    def _get_dte_section_identificacion(self, dte_document_type_id):
        if not dte_document_type_id.version:
            raise UserError(_("The document type must have a non-zero version!"))

        invoicing_model = 1
        transmission_type = 1

        if self.dte_contingency_event_id:
            invoicing_model = int(dte_document_type_id.invoicing_model)
            transmission_type = int(dte_document_type_id.transmission_type)

        if not self.dte_stamp_received:
            issue_time = datetime.now(timezone("America/El_Salvador"))
            self.dte_issue_time = issue_time.strftime("%H:%M:%S")

        values = {
            "version": dte_document_type_id.version,
            "ambiente": self.company_id.l10n_sv_destination_environment,
            "tipoDte": dte_document_type_id.code,
            "numeroControl": self._get_dte_control_number(dte_document_type_id),
            "codigoGeneracion": self._get_dte_generation_code(),
            "tipoModelo": invoicing_model,
            "tipoOperacion": transmission_type,
            "tipoContingencia": int(self.dte_contingency_event_id.type) or None,
            "fecEmi": str(self.invoice_date),
            "horEmi": self.dte_issue_time,
            "tipoMoneda": "USD",
        }

        if dte_document_type_id.code != "11":
            values["motivoContin"] = self.dte_contingency_event_id.reason or None
        else:
            values["motivoContigencia"] = self.dte_contingency_event_id.reason or None

        return values

    def _get_dte_section_documentoRelacionado(self):
        msg1 = _(
            "You cannot link an invoice with a status other than 'Posted' to the DTE."
        )
        msg2 = _(
            "You cannot link an invoice with a DTE with state of 'DTE Rejected' to the DTE."
        )
        document_id = self.reversed_entry_id or self.debit_origin_id

        if not document_id:
            return None

        if document_id.state != "posted":
            raise UserError(msg1)

        if document_id.dte_state == "dte_rejected":
            raise UserError(msg2)

        related_document = document_id.dte_generation_code or document_id.name

        return [
            {
                "tipoDocumento": document_id.journal_id.dte_document_type_id.code,
                "tipoGeneracion": 2 if document_id.dte_control_number else 1,
                "numeroDocumento": related_document,
                "fechaEmision": str(document_id.invoice_date),
            }
        ]

    def _get_dte_section_emisor(self, dte_document_type):
        issuer_id = self.company_id.partner_id
        values = issuer_id._get_partner_values("issuer", dte_document_type)

        if dte_document_type != "14":
            values["tipoEstablecimiento"] = self.sales_point_id.branch_id.type

        if dte_document_type in ["01", "03", "04", "08", "09", "11", "14", "15"]:
            values["codEstableMH"] = None
            values["codEstable"] = self.sales_point_id.branch_id.code
            values["codPuntoVentaMH"] = None
            values["codPuntoVenta"] = self.sales_point_id.code

        if dte_document_type == "07":
            values["codigoMH"] = None
            values["codigo"] = self.sales_point_id.branch_id.code
            values["puntoVentaMH"] = None
            values["puntoVenta"] = self.sales_point_id.code

        if dte_document_type == "11":
            line_ids = self.line_ids
            line_ids = line_ids.filtered(lambda l: l.display_type in ["product"])
            product_false = line_ids.filtered(lambda l: not l.product_id)
            product_ids = line_ids.filtered(lambda l: l.product_id).mapped("product_id")
            product_service = product_ids.filtered(lambda l: l.type == "service")
            product_not_service = product_ids.filtered(lambda l: l.type != "service")
            values["tipoItemExpor"] = (
                3
                if (product_service or product_false) and product_not_service
                else (1 if product_not_service else 2)
            )
            values["recintoFiscal"] = None
            values["regimen"] = None

            if values["tipoItemExpor"] in [1, 3]:
                values["recintoFiscal"] = self.fiscal_warehouse_id.code
                values["regimen"] = self.export_regime_id.code

        return values

    def _get_dte_sections(self, dte_document_type, related_document):
        sections = {}
        section, totals = self._get_dte_section_cuerpoDocumento(
            dte_document_type, related_document
        )
        sections["cuerpoDocumento"] = section
        sections["resumen"] = self._get_dte_section_resumen(dte_document_type, totals)

        return sections

    def _get_dte_section_cuerpoDocumento(self, dte_document_type, related_document):
        values = []
        num_item = 1
        totals = {
            "totalNotSent": 0.00,
            "totalNoSuj": 0.00,
            "totalExenta": 0.00,
            "totalGravada": 0.00,
            "totalCompra": 0.00,
            "totalNoGravado": 0.00,
            "totalMontoDescu": 0.00,
            "totalMontoSujetoGrav": 0.00,
            "totalIvaRetenido": 0.00,
        }

        for line_id in self.line_ids.filtered(
            lambda l: l.display_type in ["product", "tax"]
        ):
            if (
                line_id.display_type == "tax"
                and (
                    line_id.tax_group_id.l10n_sv_code not in TAXES_SECTION2
                    or dte_document_type not in ["01", "03", "04", "05", "06"]
                )
                and dte_document_type != "07"
            ):
                continue

            if dte_document_type == "07" and (
                (
                    line_id.display_type == "tax"
                    and line_id.tax_group_id.l10n_sv_code not in TAXES_CAT006
                )
                or line_id.display_type == "product"
            ):
                continue

            item = line_id._get_item_cuerpoDocumento(
                num_item, dte_document_type, related_document
            )

            if line_id.display_type == "product":
                if dte_document_type in ["01", "03", "04", "05", "06", "08"]:
                    if item["ventaNoSuj"] and line_id.account_id.l10n_sv_unsent_account:
                        totals["totalNotSent"] += item["ventaNoSuj"] or 0.00

                        continue

                    totals["totalNoSuj"] += item["ventaNoSuj"] or 0.00
                    totals["totalExenta"] += item["ventaExenta"] or 0.00

                if dte_document_type in ["01", "03", "04", "05", "06", "08", "11"]:
                    totals["totalGravada"] += item["ventaGravada"] or 0.00

                if dte_document_type == "14":
                    if item["compra"] and line_id.account_id.l10n_sv_unsent_account:
                        totals["totalNotSent"] += item["compra"] or 0.00

                        continue

                    totals["totalCompra"] += item["compra"] or 0.00

                if dte_document_type in ["01", "03", "11"]:
                    totals["totalNoGravado"] += item["noGravado"] or 0.00

                if dte_document_type in ["01", "03", "04", "05", "06", "11", "14"]:
                    totals["totalMontoDescu"] += item["montoDescu"] or 0.00

            if dte_document_type == "07":
                totals["totalMontoSujetoGrav"] += item["montoSujetoGrav"] or 0.00
                totals["totalIvaRetenido"] += item["ivaRetenido"] or 0.00

            values.append(item)
            num_item += 1

        return values, totals

    def _get_dte_section_resumen(self, dte_document_type, totals):
        values = {}
        iva = 0.00
        total = (
            totals["totalNoSuj"]
            + totals["totalExenta"]
            + totals["totalGravada"]
            + totals["totalCompra"]
            + totals["totalNoGravado"]
        )
        total_to_pay = self.amount_total - totals["totalNotSent"]
        total_taxes = 0.00
        total_ivaRete1 = 0.00
        total_reteRenta = 0.00

        if dte_document_type in ["01", "03", "04", "05", "06", "08", "14"]:
            tributos = []

            for line_id in self.line_ids.filtered(lambda l: l.display_type in ["tax"]):
                if not line_id.tax_group_id.l10n_sv_code:
                    raise UserError(
                        _("Tax group '%s' has no code!") % line_id.tax_group_id.name
                    )

                if line_id.tax_group_id.l10n_sv_code == "20":
                    iva = abs(line_id.balance)

                    if dte_document_type == "01":
                        continue

                if line_id.tax_group_id.l10n_sv_code in TAXES_CAT006:
                    total_ivaRete1 += abs(line_id.balance)

                    continue

                if line_id.tax_group_id.l10n_sv_code == "ReteRenta":
                    total_reteRenta += abs(line_id.balance)

                    continue

                if line_id.tax_group_id.l10n_sv_code not in TAXES_SECTION2:
                    tributos.append(
                        {
                            "codigo": line_id.tax_group_id.l10n_sv_code,
                            "descripcion": line_id.tax_group_id.name,
                            "valor": abs(line_id.balance),
                        }
                    )
                    total_taxes += abs(line_id.balance)

        if dte_document_type in ["01", "03", "04", "05", "06", "08"]:
            values["totalNoSuj"] = round(totals["totalNoSuj"], 2)
            values["totalExenta"] = round(totals["totalExenta"], 2)

        if dte_document_type in ["01", "03", "04", "05", "06", "08", "11"]:
            values["totalGravada"] = round(totals["totalGravada"], 2)

        if dte_document_type == "08":
            values["exportacion"] = 0.00

        if dte_document_type == "14":
            values["totalCompra"] = round(totals["totalCompra"], 2)

        if dte_document_type == "15":
            values["valorTotal"] = 0.00

        if dte_document_type in ["01", "03", "04", "05", "06", "08"]:
            values["subTotalVentas"] = round(total, 2)

        if dte_document_type in ["01", "03", "04", "05", "06"]:
            values["descuNoSuj"] = 0.00
            values["descuExenta"] = 0.00
            values["descuGravada"] = 0.00

        if dte_document_type == "11":
            values["descuento"] = 0.00

        if dte_document_type == "14":
            values["descu"] = 0.00

        if dte_document_type in ["01", "03", "04", "11"]:
            values["porcentajeDescuento"] = 0.00

        if dte_document_type in ["01", "03", "04", "05", "06", "11", "14"]:
            values["totalDescu"] = round(totals["totalMontoDescu"], 2)

        if dte_document_type in ["01", "03", "04", "05", "06", "08"]:
            values["tributos"] = tributos or None

        if dte_document_type in ["01", "03", "04", "05", "06", "14"]:
            values["subTotal"] = round(total, 2)

        if dte_document_type == "07":
            values["totalSujetoRetencion"] = round(totals["totalMontoSujetoGrav"], 2)

        if dte_document_type in ["03", "05", "06"]:
            values["ivaPerci1"] = 0.00

        if dte_document_type == "08":
            values["ivaPerci"] = 0.00

        if dte_document_type in ["01", "03", "05", "06", "14"]:
            values["ivaRete1"] = round(total_ivaRete1, 2)
            values["reteRenta"] = round(total_reteRenta, 2)

        if dte_document_type == "11":
            values["seguro"] = 0.00
            values["flete"] = 0.00

        if dte_document_type in ["01", "03", "04", "05", "06", "08", "11"]:
            values["montoTotalOperacion"] = round(total + total_taxes, 2)

        if dte_document_type in ["01", "03", "11"]:
            values["totalNoGravado"] = round(totals["totalNoGravado"], 2)

        if dte_document_type in ["01", "03", "11", "14"]:
            values["totalPagar"] = round(total_to_pay, 2)

        if dte_document_type == "08":
            values["total"] = 0.00

        if dte_document_type == "07":
            total = round(totals["totalIvaRetenido"], 2)
            values["totalIVAretenido"] = total
            values["totalIVAretenidoLetras"] = self._get_value_in_letters(total)

        if dte_document_type in ["01", "03", "04", "05", "06", "08", "11", "14", "15"]:
            values["totalLetras"] = self._get_value_in_letters(total_to_pay)

        if dte_document_type == "01":
            values["totalIva"] = round(iva, 2)

        if dte_document_type in ["01", "03"]:
            values["saldoFavor"] = 0.00

        if dte_document_type in ["01", "03", "05", "06", "08", "11", "14"]:
            condition = 3 if not self.invoice_date_due else 2
            condition = 1 if self.invoice_date == self.invoice_date_due else condition
            values["condicionOperacion"] = condition

        # TODO
        if dte_document_type in ["01", "03", "11", "14", "15"]:
            pagos = []

            for pago in pagos:
                pagos_values = {
                    "codigo": "99",
                    "montoPago": pago.montoPago,
                    "Referencia": None,
                }

                if dte_document_type in ["01", "03", "11", "14"]:
                    pagos_values["plazo"] = None
                    pagos_values["periodo"] = None

                pagos.append(pagos_values)

            values["pagos"] = pagos or None

        if dte_document_type in ["01", "03", "06", "11"]:
            values["numPagoElectronico"] = None

        if dte_document_type == "11":
            values["codIncoterms"] = (
                self.invoice_incoterm_id.l10n_sv_document_code or None
            )
            values["descIncoterms"] = self.invoice_incoterm_id.name or None

        if dte_document_type in ["11", "14"]:
            values["observaciones"] = None

        return values

    def _get_dte_section_extension(self, dte_document_type):
        issuer_id = self.company_id.partner_id
        receiver_id = self.partner_id
        values = {}

        if dte_document_type in ["01", "03", "04", "05", "06", "07", "08", "09"]:
            values["nombEntrega"] = issuer_id.name
            values["docuEntrega"] = issuer_id._get_partner_vat()

        if dte_document_type == "09":
            values["codEmpleado"] = None

        if dte_document_type in ["01", "03", "04", "05", "06", "07", "08"]:
            values["nombRecibe"] = receiver_id.name
            values["docuRecibe"] = receiver_id._get_partner_vat()

        if dte_document_type in ["01", "03"]:
            values["placaVehiculo"] = None

        if dte_document_type in ["01", "03", "04", "05", "06", "07", "08"]:
            values["observaciones"] = None

        return values or None

    def _get_dte_section_apendice(self):
        values = []
        field_count = 1
        fields = []  # TODO

        for field in fields:
            if field_count > 10:
                raise UserError(_("You can only add 10 fields maximum.!"))

            field_count += 1
            values.append({"campo": None, "etiqueta": None, "valor": None})

        return values or None

    def _get_dte_signed_json(self, dte_document_type_id):
        dte_document_type = dte_document_type_id.code

        if dte_document_type not in DOCUMENT_TYPES:
            return {}

        unsigned_json = {
            "identificacion": self._get_dte_section_identificacion(
                dte_document_type_id
            ),
        }
        related_document = self._get_dte_section_documentoRelacionado()

        if dte_document_type in ["01", "03", "04", "05", "06"]:
            unsigned_json["documentoRelacionado"] = related_document

        if related_document:
            related_document = related_document[0]["numeroDocumento"]

        if dte_document_type in ["07", "08"]:
            related_document = self.ref

        unsigned_json["emisor"] = self._get_dte_section_emisor(dte_document_type)
        receiver = self.partner_id._get_partner_values("receiver", dte_document_type)

        if dte_document_type in ["01", "03", "04", "05", "06", "07", "11"]:
            unsigned_json["receptor"] = receiver

        if dte_document_type == "14":
            unsigned_json["sujetoExcluido"] = receiver

        if dte_document_type in ["01", "03", "11", "15"]:
            unsigned_json["otrosDocumentos"] = None

        if dte_document_type in ["01", "03", "04", "05", "06", "11"]:
            unsigned_json["ventaTercero"] = None

        sections = self._get_dte_sections(dte_document_type, related_document)
        unsigned_json["cuerpoDocumento"] = sections["cuerpoDocumento"]
        unsigned_json["resumen"] = sections["resumen"]

        if dte_document_type in ["01", "03", "04", "05", "06", "07", "08", "09"]:
            unsigned_json["extension"] = self._get_dte_section_extension(
                dte_document_type
            )

        unsigned_json["apendice"] = self._get_dte_section_apendice()
        signed_json = self.company_id.action_post_signer(unsigned_json)
        unsigned_json["firmaElectronica"] = signed_json

        return unsigned_json

    def action_set_dte_json(self, signed_json=None, recreate=False):
        json_name = "%s.json" % (self.dte_generation_code.replace("/", "_"))
        json_attachment_id = self.env["ir.attachment"].search(
            [("name", "=", json_name), ("res_id", "in", [self.id])]
        )

        if not json_attachment_id or recreate:
            if json_attachment_id:
                json_attachment_id.unlink()

            if not signed_json:
                signed_json = self._get_dte_signed_json(self.dte_document_type_id)

            signed_json["selloRecibido"] = self.dte_stamp_received or None
            json_dump = dumps(signed_json)
            json_name = "%s.json" % (self.dte_generation_code.replace("/", "_"))
            json_attachment_id = self.env["ir.attachment"].create(
                {
                    "name": json_name,
                    "raw": json_dump.encode(),
                    "res_model": "account.move",
                    "res_id": self.id,
                    "mimetype": "application/json",
                }
            )

        return json_attachment_id

    def action_post_recepciondte(self):
        signed_json = self._get_dte_signed_json(self.dte_document_type_id)
        response_recepciondte = self.company_id._execute_api_request(
            "fesv/recepciondte",
            {
                "ambiente": self.company_id.l10n_sv_destination_environment,
                "idEnvio": "1",
                "version": self.dte_document_type_id.version,
                "tipoDte": self.dte_document_type_id.code,
                "documento": signed_json["firmaElectronica"],
                "codigoGeneracion": self.dte_generation_code,
            },
        )
        stamp_received = response_recepciondte.get("selloRecibido")
        self.write(
            {
                "dte_state": "dte_transmitted" if stamp_received else "dte_rejected",
                "dte_stamp_received": stamp_received,
                "response_recepciondte": response_recepciondte,
            }
        )
        self.action_set_dte_json(signed_json, True)

        if stamp_received:
            if self.company_id.l10n_sv_automatic_email_sending:
                self.action_send_dte_email()
        else:
            self.action_send_dte_error_email()

    def action_post_consultadte(self):
        response_consultadte = self.company_id._execute_api_request(
            "fesv/recepcion/consultadte/",
            {
                "nitEmisor": self.company_id.partner_id._get_partner_vat(),
                "tdte": self.dte_document_type_id.code,
                "codigoGeneracion": self.dte_generation_code,
            },
        )
        stamp_received = response_consultadte.get("selloRecibido")
        self.write(
            {
                "dte_state": "dte_transmitted" if stamp_received else "dte_rejected",
                "dte_stamp_received": stamp_received,
                "response_consultadte": response_consultadte,
            }
        )

    def action_send_email(self, ref):
        mail_template_id = self.env.ref(ref)
        mail_id = mail_template_id.send_mail(self.id, force_send=True)

        return self.env["mail.mail"].browse(mail_id)

    def action_send_dte_email(self):
        if not self.partner_id.email:
            self.action_send_dte_error_email()

            return

        mail_id = self.action_send_email("l10n_sv_edi.mail_template_dte")

        if mail_id.state == "sent":
            self.dte_sent_by_email = True
            mail_id.sudo().unlink()

    def action_send_dte_error_email(self):
        if not self.company_id.l10n_sv_dte_error_email:
            return

        mail_id = self.action_send_email("l10n_sv_edi.mail_template_dte_error")

        if mail_id.state == "sent":
            mail_id.sudo().unlink()

    def _get_invalidation_section_identificacion(self):
        if not self.dte_invalidation_generation_code:
            self.dte_invalidation_generation_code = str(uuid4()).upper()

        issue_time = datetime.now(timezone("America/El_Salvador"))

        return {
            "version": 2,
            "ambiente": self.company_id.l10n_sv_destination_environment,
            "codigoGeneracion": self.dte_invalidation_generation_code,
            "fecAnula": str(fields.Date.today()),
            "horAnula": issue_time.strftime("%H:%M:%S"),
        }

    def _get_invalidation_section_emisor(self):
        values = self.company_id.partner_id._get_partner_values("issuer")
        values["tipoEstablecimiento"] = self.sales_point_id.branch_id.type
        values["nomEstablecimiento"] = self.sales_point_id.branch_id.name
        values["codEstableMH"] = None
        values["codEstable"] = self.sales_point_id.branch_id.code
        values["codPuntoVentaMH"] = None
        values["codPuntoVenta"] = self.sales_point_id.code

        return values

    def _get_invalidation_section_documento(self):
        iva = 0.00

        for line_id in self.line_ids.filtered(lambda l: l.display_type in ["tax"]):
            if line_id.tax_group_id.l10n_sv_code == "20":
                iva = abs(line_id.balance)

        values = self.partner_id._get_partner_values("receiver")
        values |= {
            "tipoDte": self.dte_document_type_id.code,
            "codigoGeneracion": self.dte_generation_code,
            "selloRecibido": self.dte_stamp_received,
            "numeroControl": self.dte_control_number,
            "fecEmi": str(self.invoice_date),
            "montoIva": round(iva, 2),
            # "monto": round(self.amount_total, 2),
            "codigoGeneracionR": self.dte_invalidation_move_id.dte_generation_code
            or None,
        }

        return values

    def _get_invalidation_section_motivo(self):
        return {
            "tipoAnulacion": int(self.dte_invalidation_type),
            "motivoAnulacion": self.dte_invalidation_reason,
            "nombreResponsable": self.env.user.partner_id.name,
            "tipDocResponsable": self.env.user.partner_id.l10n_latam_identification_type_id.l10n_sv_document_code
            or "13",
            "numDocResponsable": self.env.user.partner_id._get_partner_vat(),
            "nombreSolicita": self.partner_id.name,
            "tipDocSolicita": self.partner_id.l10n_latam_identification_type_id.l10n_sv_document_code
            or "13",
            "numDocSolicita": self.partner_id._get_partner_vat(),
        }

    def _get_invalidation_signed_json(self):
        unsigned_json = {
            "identificacion": self._get_invalidation_section_identificacion(),
        }
        unsigned_json["emisor"] = self._get_invalidation_section_emisor()
        unsigned_json["documento"] = self._get_invalidation_section_documento()
        unsigned_json["motivo"] = self._get_invalidation_section_motivo()

        return self.company_id.action_post_signer(unsigned_json)

    def action_post_anulardte(self):
        response_anulardte = self.company_id._execute_api_request(
            "fesv/anulardte",
            {
                "ambiente": self.company_id.l10n_sv_destination_environment,
                "idEnvio": "1",
                "version": 2,
                "documento": self._get_invalidation_signed_json(),
            },
        )
        stamp_received = response_anulardte.get("selloRecibido")
        self.write(
            {
                "dte_state": (
                    "dte_invalidated" if stamp_received else "dte_invalidation_rejected"
                ),
                "dte_invalidation_stamp_received": stamp_received,
                "response_anulardte": response_anulardte,
            }
        )
