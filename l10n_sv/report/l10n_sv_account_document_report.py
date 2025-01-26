# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import sql
from odoo import fields, models, tools


class L10nSvAccountDocumentReport(models.Model):
    _name = "l10n_sv_account.document.report"
    _description = "Documents Report"
    _auto = False
    _order = "date"

    date = fields.Date(string="Date of Issue")
    code = fields.Char(string="Document")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    taxpayer_registration_number = fields.Char(string="Taxpayer Registration Number")
    internal_exempt_purchases = fields.Float(string="Internal Exempt Purchases")
    internal_taxable_purchases = fields.Float(string="Internal Taxable Purchases")
    external_taxable_purchases = fields.Float(string="External Taxable Purchases")
    fovial = fields.Float(string="FOVIAL")
    vat = fields.Float(string="VAT")
    total = fields.Float(string="Total")
    operation_type = fields.Char(string="Operation Type")
    classification = fields.Selection(
        selection=[("expense", "Expense"), ("cost", "Cost")], string="Classification"
    )
    classification_type = fields.Selection(
        selection=[
            ("sales", "Sales"),
            ("admin", "Admin"),
            ("financial", "Financial"),
            ("cost", "Cost"),
        ],
        string="Classification Type",
    )
    l10n_sv_account_document_class_id = fields.Many2one(
        comodel_name="l10n_sv_account.document.class", string="Document Class"
    )
    l10n_sv_account_document_type_id = fields.Many2one(
        comodel_name="l10n_sv_account.document.type", string="Document Type"
    )

    def init(self):
        query = """
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY
                        LSAD.date,
                        LSAD.code
                ) id,
                LSAD.date,
                LSAD.code,
                LSAD.partner_id,
                NRC.name taxpayer_registration_number,
                SUM(
                    CASE
                        WHEN AA.l10n_sv_is_internal_exempt_purchase THEN AML.balance
                        ELSE 0
                    END
                ) internal_exempt_purchases,
                SUM(
                    CASE
                        WHEN AA.l10n_sv_is_internal_vat_tax THEN ROUND(AML.balance * 100 / 13, 2)
                        ELSE 0
                    END
                ) internal_taxable_purchases,
                SUM(
                    CASE
                        WHEN AA.l10n_sv_is_external_vat_tax THEN ROUND(AML.balance * 100 / 13, 2)
                        ELSE 0
                    END
                ) external_taxable_purchases,
                SUM(
                    CASE
                        WHEN AA.l10n_sv_is_fovial_tax THEN AML.balance
                        ELSE 0
                    END
                ) fovial,
                SUM(
                    CASE
                        WHEN AA.l10n_sv_is_internal_vat_tax
                        OR AA.l10n_sv_is_external_vat_tax THEN AML.balance
                        ELSE 0
                    END
                ) vat,
                SUM(
                    CASE
                        WHEN AA.l10n_sv_is_internal_exempt_purchase
                        OR AA.l10n_sv_is_fovial_tax THEN AML.balance
                        WHEN AA.l10n_sv_is_internal_vat_tax
                        OR AA.l10n_sv_is_external_vat_tax THEN AML.balance + ROUND(AML.balance * 100 / 13, 2)
                        ELSE 0
                    END
                ) total,
                'GRAVADA' operation_type,
                LSAD.classification,
                LSAD.classification_type,
                LSAD.l10n_sv_account_document_class_id,
                LSAD.l10n_sv_account_document_type_id
            FROM
                account_move_line AML
                INNER JOIN account_account AA ON (AML.account_id = AA.id)
                LEFT JOIN l10n_sv_account_document LSAD ON (AML.l10n_sv_account_document_id = LSAD.id)
                LEFT JOIN (
                    SELECT
                        RPIN.partner_id,
                        RPIN.name
                    FROM
                        res_partner_id_number RPIN
                        INNER JOIN res_partner_id_category RPIC ON (RPIN.category_id = RPIC.id)
                    WHERE
                        RPIC.code = 'nrc'
                ) NRC ON (LSAD.partner_id = NRC.partner_id)
            WHERE
                AA.l10n_sv_is_internal_exempt_purchase
                OR AA.l10n_sv_is_internal_vat_tax
                OR AA.l10n_sv_is_external_vat_tax
                OR AA.l10n_sv_is_fovial_tax
            GROUP BY
                LSAD.date,
                LSAD.code,
                LSAD.partner_id,
                LSAD.classification,
                LSAD.classification_type,
                LSAD.l10n_sv_account_document_class_id,
                LSAD.l10n_sv_account_document_type_id,
                NRC.name
            ORDER BY
                LSAD.date,
                LSAD.code
        """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            sql.SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                sql.Identifier(self._table), sql.SQL(query)
            )
        )
