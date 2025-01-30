# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Stock Location Position Product",
    "version": "14.0.1.0.0",
    "category": "Warehouse",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "maintainers": ["joanmarin"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "views/stock_location_position_views.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
        "views/stock_inventory_line_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
