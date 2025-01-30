# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from psycopg2 import sql
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    last_purchase_order_id = fields.Many2one(
        string="Last Purchase Order", comodel_name="purchase.order"
    )

    def action_update_last_purchase_order_id(self):
        self.env.cr.execute(
            sql.SQL(
                """
                UPDATE
                    product_template PT
                SET
                    last_purchase_order_id = CONSULTA.last_purchase_order_id
                FROM
                    (
                        SELECT
                            PP.product_tmpl_id,
                            MAX(POL.order_id) last_purchase_order_id
                        FROM
                            purchase_order_line POL
                            INNER JOIN product_product PP ON (POL.product_id = PP.id)
                        WHERE
                            POL.state in ('purchase', 'done')
                        GROUP BY
                            PP.product_tmpl_id
                    ) CONSULTA
                WHERE
                    PT.id = CONSULTA.product_tmpl_id
                """
            )
        )
