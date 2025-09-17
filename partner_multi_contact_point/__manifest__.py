# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Partner Multi Contact Point",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/partner-contact",
    "author": "EXA Auto Parts Github@exaap, "
    "Joan Marín Github@JoanMarin, "
    "Odoo Community Association (OCA)",
    "maintainers": ["joanmarin"],
    "category": "Partner Management",
    "depends": [
        "contacts",
        "partner_contact_job_position",
        "partner_phone_extension",
        "phone_validation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_contact_point_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
