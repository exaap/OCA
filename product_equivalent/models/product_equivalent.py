# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProductEquivalent(models.Model):
    _name = "product.equivalent"
    _description = "Equivalent Products"

    manufacturer_pref = fields.Char(string="Manuf. Product Code", required=True)
    manufacturer_pname = fields.Char(string="Manuf. Product Name")
    brand_id = fields.Many2one(
        string="Brand",
        comodel_name="product.brand",
        required=False,
    )
    manufacturer_id = fields.Many2one(
        string="Manufacturer",
        comodel_name="res.partner",
        required=False,
        domain=[("is_manufacturer", "=", True)],
    )
    product_id = fields.Many2one(string="Product", comodel_name="product.product")
    product_equivalent_group_ids = fields.Many2many(
        comodel_name="product.equivalent.group",
        relation="product_equivalent_group_product_equivalent_rel",
        column1="product_equivalent_id",
        column2="product_equivalent_group_id",
        string="Groups of Equivalent Products",
    )
    product_template_ids = fields.Many2many(
        comodel_name="product.template",
        string="Related Products",
        compute="_compute_product_template_ids",
        store=False,
    )
    product_template_id = fields.Many2one(
        string="Product Template", comodel_name="product.template"
    )

    @api.depends("product_equivalent_group_ids")
    def _compute_product_template_ids(self):
        for equivalent_id in self:
            product_template_ids = equivalent_id.product_equivalent_group_ids.mapped(
                "product_template_ids"
            )
            equivalent_id.product_template_ids = product_template_ids

    def name_get(self):
        res = []

        for record in self:
            if record.manufacturer_id:
                name = "[%s] %s" % (
                    record.manufacturer_id.name or "",
                    record.manufacturer_pref or "",
                )
            else:
                name = "%s" % (record.manufacturer_pref or "")

            res.append((record.id, name))

        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []

        if name:
            args = [("manufacturer_pref", operator, name)] + args

        return self.search(args, limit=limit).name_get()

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for record in self:
            record.brand_id = record.product_id.product_tmpl_id.product_brand_id
            record.manufacturer_id = record.product_id.product_tmpl_id.manufacturer
            record.manufacturer_pref = (
                record.product_id.product_tmpl_id.manufacturer_pref
            )
            record.manufacturer_pname = (
                record.product_id.product_tmpl_id.manufacturer_pname
            )
