# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models

TAXES_SECTION2 = ["A8", "57", "90", "D4", "D5", "A6"]
TAXES_CAT006 = ["22", "C4", "C9"]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_item_cuerpoDocumento(self, num_item, dte_document_type, related_document):
        values = {}
        price_unit = self.price_unit
        discount = self.quantity * price_unit * self.discount / 100
        total = self.quantity * price_unit - discount

        if dte_document_type != "09":
            values["numItem"] = num_item

        if dte_document_type in ["01", "03", "04", "05", "06", "14"]:
            values["tipoItem"] = (
                4
                if self.display_type == "tax"
                else (
                    2 if not self.product_id or self.product_id.type == "service" else 1
                )
            )

        if dte_document_type == "15":
            values["tipoDonacion"] = (
                "1"
                if not self.product_id
                else ("3" if self.product_id.type == "service" else "2")
            )
            values["tipoDepreciacion"] = 0.00

        if dte_document_type in ["07", "08"]:
            values["tipoDte"] = self.move_id.supplier_dte_document_type_id.code or None
            values["tipoDoc"] = 2 if self.move_id.dte_control_number else 1

        if dte_document_type in ["01", "03", "04", "05", "06", "08"]:
            values["numeroDocumento"] = related_document

        if dte_document_type == "07":
            values["numDocumento"] = related_document

        if dte_document_type in ["07", "08"]:
            values["fechaEmision"] = str(self.move_id.invoice_date)

        if dte_document_type in ["01", "03", "04", "05", "06", "11", "14", "15"]:
            values["cantidad"] = round(self.quantity or 1, 8)
            values["codigo"] = None

        if dte_document_type in ["01", "03", "04", "05", "06"]:
            values["codTributo"] = (
                self.tax_group_id.l10n_sv_code if self.tax_group_id else None
            )

        if dte_document_type in ["01", "03", "04", "05", "06", "11", "14", "15"]:
            values["uniMedida"] = self.product_uom_id.code or 99

        if dte_document_type in ["01", "03", "04", "05", "06", "07", "11", "14", "15"]:
            values["descripcion"] = (
                self.product_id.name if self.product_id else self.name
            )

        if dte_document_type in ["01", "03", "04", "05", "06", "08", "11"]:
            tributos = []
            iva = 0.00

            for tax_id in self.tax_ids:
                if tax_id.tax_group_id.l10n_sv_code == "20":
                    tax_percentage = tax_id.amount / 100
                    iva = total * tax_percentage

                    if dte_document_type == "01":
                        total += iva
                        price_unit += (
                            price_unit - discount / self.quantity
                        ) * tax_percentage

                        continue

                if tax_id.tax_group_id.l10n_sv_code in TAXES_CAT006:
                    continue

                if tax_id.tax_group_id.l10n_sv_code == "ReteRenta":
                    continue

                if tax_id.tax_group_id.l10n_sv_code not in TAXES_SECTION2:
                    tributos.append(tax_id.tax_group_id.l10n_sv_code)

        total = round(total, 8)

        if dte_document_type in ["01", "03", "04", "05", "06", "11", "14"]:
            values["precioUni"] = round(price_unit, 8)

        if dte_document_type == "15":
            values["valorUni"] = round(price_unit, 8)

        if dte_document_type in ["01", "03", "04", "05", "06", "11", "14"]:
            values["montoDescu"] = round(discount, 8)

        if dte_document_type in ["01", "03", "04", "05", "06", "08"]:
            values["ventaNoSuj"] = total if not iva else 0.00
            values["ventaExenta"] = 0.00

        if dte_document_type in ["01", "03", "04", "05", "06", "08", "11"]:
            values["ventaGravada"] = total if iva or dte_document_type == "11" else 0.00

        if dte_document_type == "08":
            values["exportaciones"] = 0.00

        if dte_document_type == "15":
            values["valor"] = round(self.quantity * price_unit, 8)

        if dte_document_type == "14":
            values["compra"] = total

        if dte_document_type in ["01", "03", "04", "05", "06", "08", "11"]:
            values["tributos"] = tributos or None

        if dte_document_type in ["01", "03"]:
            values["psv"] = 0.00

        if dte_document_type in ["01", "03", "11"]:
            values["noGravado"] = 0.00

        if dte_document_type in ["01", "08"]:
            values["ivaItem"] = round(iva, 8)

        if dte_document_type == "07":
            values["montoSujetoGrav"] = self.balance * 100 / self.tax_line_id.amount
            values["codigoRetencionMH"] = self.tax_group_id.l10n_sv_code
            values["ivaRetenido"] = abs(self.balance)

        if dte_document_type == "09":
            values["periodoLiquidacionFechaInicio"] = None
            values["periodoLiquidacionFechaFin"] = None
            values["codigoLiquidacion"] = None
            values["cantidadDoc"] = None
            values["valorOperaciones"] = 0.00
            values["montoSinPercepcion"] = 0.00
            values["descripcionPercepcion"] = None

        if dte_document_type == "08":
            values["obsItem"] = None

        if dte_document_type == "09":
            values["observaciones"] = None
            values["subTotal"] = 0.00
            values["IVA"] = 0.00
            values["montoSujetoPercepcion"] = 0.00
            values["IVApercibido"] = 0.00
            values["comision"] = 0.00
            values["porcentComision"] = 0.00
            values["IVAcomision"] = 0.00
            values["liquidoApagar"] = 0.00

        if dte_document_type == "08":
            values["totalLetras"] = None

        return values
