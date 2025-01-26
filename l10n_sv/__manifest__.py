# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "El Salvador - Accounting",
    "version": "16.0.1.0.0",
    "category": "Localization",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-el-salvador",
    "depends": [
        "account",
        "partner_identification",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/l10n_sv_account.document.class.csv",
        "data/l10n_sv_account.document.type.csv",
        "data/res.partner.id_category.csv",
        "views/account_account_views.xml",
        "views/account_move_line_views.xml",
        "views/l10n_sv_account_document_class_views.xml",
        "views/l10n_sv_account_document_type_views.xml",
        "views/l10n_sv_account_document_views.xml",
        "views/res_partner_views.xml",
        "report/l10n_sv_account_document_report_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
