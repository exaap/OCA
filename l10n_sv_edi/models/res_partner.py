# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_partner_vat(self, dte_document_type=None):
        if not self.vat:
            raise UserError(
                _("%s does not have an identification number!") % self.display_name
            )

        vat = self.vat.replace(self.country_id.code or "", "").replace("-", "")

        if self.l10n_latam_identification_type_id.l10n_sv_document_code == "13":
            if dte_document_type not in ["03", "05", "14"]:
                vat = vat[:-1] + "-" + vat[-1:]

        return vat

    def _get_partner_values(self, partner_type, dte_document_type=None):
        values = {}
        nrc = self.taxpayer_registration_number
        nrc = nrc.replace("-", "") if nrc else None
        vat = self._get_partner_vat(dte_document_type)
        industry_name = self.industry_id.name[:150] if self.industry_id else None
        street = [self.street, self.street2, self.district_id.name]
        street = "/".join(filter(None, street)) or None
        phone = "/".join(filter(None, [self.mobile, self.phone]))
        address = {"departamento": "00", "municipio": "00", "complemento": street}
        domiciled_code = "2"

        if self.country_id and self.country_id.code == "SV":
            address["departamento"] = self.zip_id.state_id.code or None
            address["municipio"] = self.zip_id.city_id.code or None
            domiciled_code = "1"

        if partner_type == "issuer":
            if dte_document_type != "15":
                values["nit"] = vat

            if dte_document_type == "15":
                values["tipoDocumento"] = "36"
                values["numDocumento"] = vat

            if dte_document_type:
                values["nrc"] = nrc

            values["nombre"] = self.name

            if dte_document_type:
                values["codActividad"] = self.industry_id.code
                values["descActividad"] = industry_name

            if dte_document_type not in ["14", None]:
                values["nombreComercial"] = self.commercial_name or None

            if dte_document_type:
                values["direccion"] = address

        if partner_type == "receiver":
            if dte_document_type in ["01", "04", "07", "11", "14", "15", None]:
                values["tipoDocumento"] = (
                    self.l10n_latam_identification_type_id.l10n_sv_document_code or "13"
                )
                values["numDocumento"] = vat

            if dte_document_type in ["03", "05", "06", "08", "09"]:
                values["nit"] = vat

            if dte_document_type not in ["11", "14", None]:
                values["nrc"] = nrc

            values["nombre"] = self.name

            if dte_document_type not in ["11", None]:
                values["codActividad"] = self.industry_id.code or None

            if dte_document_type:
                values["descActividad"] = industry_name

            if dte_document_type in ["03", "04", "05", "06", "07", "08", "09", "11"]:
                values["nombreComercial"] = self.commercial_name or None

            if dte_document_type == "09":
                values["tipoEstablecimiento"] = "02"

            if dte_document_type not in ["11", None]:
                values["direccion"] = address

            if dte_document_type == "11":
                values["complemento"] = street

            if dte_document_type in ["11", "15"]:
                values["codPais"] = self.country_id.code

            if dte_document_type == "11":
                values["nombrePais"] = self.country_id.name

            if dte_document_type == "15":
                values["codDomiciliado"] = domiciled_code

            if dte_document_type == "09":
                values["codigoMH"] = None
                values["puntoVentaMH"] = None

            if dte_document_type == "04":
                values["bienTitulo"] = "01"

            if dte_document_type == "11":
                values["tipoPersona"] = 1 if self.company_type == "person" else 2

        values["telefono"] = phone[:30] if phone else None
        values["correo"] = self.email or None

        return values
