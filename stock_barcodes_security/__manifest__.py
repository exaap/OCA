# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Stock Barcodes Security",
    "version": "12.0.1.0.0",
    "category": "Extra Tools",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "maintainers": ["joanmarin"],
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "depends": [
        "stock_barcodes",
    ],
    "data": [
        "security/res_groups.xml",
        "wizard/wiz_stock_barcodes_read_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
