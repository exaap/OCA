# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProductEquivalentGrouo(models.Model):
    _name = "product.equivalent.group"
    _description = "Groups of Equivalent Products"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    brand_id = fields.Many2one(string="Brand", comodel_name="product.brand")
    manufacturer_id = fields.Many2one(
        string="Manufacturer",
        comodel_name="res.partner",
        domain=[("is_manufacturer", "=", True)],
    )
    product_equivalent_ids = fields.Many2many(
        comodel_name="product.equivalent",
        relation="product_equivalent_group_product_equivalent_rel",
        column1="product_equivalent_group_id",
        column2="product_equivalent_id",
        string="Equivalent Products",
    )
    product_template_ids = fields.One2many(
        comodel_name="product.template",
        inverse_name="product_equivalent_group_id",
        string="Product Templates",
    )

    def name_get(self):
        res = []

        for record in self:
            if record.code:
                name = "[%s] %s" % (record.code or "", record.name or "")
            else:
                name = "%s" % (record.name or "")

            res.append((record.id, name))

        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []

        if name:
            args = [("code", operator, name)] + args

        return self.search(args, limit=limit).name_get()
