# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Base Location District",
    "version": "16.0.1.0.0",
    "category": "Partner Management",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "maintainers": ["joanmarin"],
    "website": "https://github.com/OCA/partner-contact",
    "depends": [
        "base_location",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_city_zip_district_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
