# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "El Salvador - E-invoicing",
    "version": "16.0.1.0.0",
    "category": "Accounting/Localizations/EDI",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-el-salvador",
    "depends": [
        "account_debit_note",
        "account_move_name_sequence",
        "base_multi_branch_company",
        "partner_commercial_name",
        "l10n_sv",
        "l10n_sv_base_location_district",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account.incoterms.csv",
        "data/account.tax.group.csv",
        "data/l10n_sv_account.document.class.csv",
        "data/l10n_sv_account.document.type.csv",
        "data/l10n_sv_export.regime.csv",
        "data/l10n_sv_fiscal.warehouse.csv",
        "data/res.branch.csv",
        "data/res.sales.point.csv",
        "data/uom.uom.csv",
        "report/ir_actions_report.xml",
        "report/mail_template.xml",
        "views/account_account_views.xml",
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "views/account_tax_group_views.xml",
        "views/l10n_sv_dte_contingency_event_views.xml",
        "views/res_branch_views.xml",
        "views/res_company_views.xml",
        "views/res_sales_point_views.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
}
