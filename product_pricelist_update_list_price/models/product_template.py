# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from psycopg2 import sql
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_update_list_price(self):
        self.env.cr.execute(
            sql.SQL(
                """
                UPDATE
                    product_template PT
                SET
                    list_price = CONSULTA.list_price
                FROM
                    (
                        SELECT
                            PP.product_tmpl_id,
                            -1 * (-100 + PPLI.price_discount) / 100 * PSP.standard_price list_price
                        FROM
                            product_pricelist_item PPLI
                            INNER JOIN product_pricelist PPL ON (PPLI.pricelist_id = PPL.id)
                            INNER JOIN product_template PT ON (PPLI.categ_id = PT.categ_id)
                            INNER JOIN product_product PP ON (PT.id = PP.product_tmpl_id)
                            LEFT JOIN (
                                SELECT
                                    ROUND(CAST(value_float AS NUMERIC), 2) standard_price,
                                    CAST(SUBSTRING(res_id, 17) AS INTEGER) product_id
                                FROM
                                    ir_property IP
                                WHERE
                                    NAME = 'standard_price'
                            ) PSP ON (PP.id = PSP.product_id)
                        WHERE
                            PPL.update_list_price = True
                            AND PPLI.compute_price = 'formula'
                            AND PPLI.base = 'standard_price'
                            AND applied_on = '2_product_category'
                            AND PT.active = True
                            AND PT.type = 'product'
                            AND PSP.standard_price IS NOT NULL
                            AND PSP.standard_price > 0
                    ) CONSULTA
                WHERE
                    PT.id = CONSULTA.product_tmpl_id
                """
            )
        )
