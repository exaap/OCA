# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Purchase Last Order",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "maintainers": ["joanmarin"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/product_product_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
