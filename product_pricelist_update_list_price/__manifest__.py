# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Product Pricelist Update List Price",
    "version": "16.0.1.0.0",
    "category": "Product",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "maintainers": ["joanmarin"],
    "website": "https://github.com/OCA/product-attribute",
    "depends": [
        "sale_management",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/product_pricelist_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
