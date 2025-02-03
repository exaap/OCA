# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from openupgradelib import openupgrade


def fill_stock_move_zero_inventory(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO
            STOCK_MOVE (
                NAME,
                SEQUENCE,
                PRIORITY,
                DATE,
                COMPANY_ID,
                PRODUCT_ID,
                PRODUCT_QTY,
                PRODUCT_UOM_QTY,
                PRODUCT_UOM,
                LOCATION_ID,
                LOCATION_DEST_ID,
                STATE,
                PROCURE_METHOD,
                PROPAGATE_CANCEL,
                IS_INVENTORY,
                REFERENCE,
                CREATE_UID,
                CREATE_DATE,
                WRITE_UID,
                WRITE_DATE,
                INVENTORY_ID
            )
        SELECT
            'FV:' || SI.NAME NAME,
            10 SEQUENCE,
            1 PRIORITY,
            SI.DATE,
            SIL.COMPANY_ID,
            SIL.PRODUCT_ID,
            0 PRODUCT_QTY,
            0 PRODUCT_UOM_QTY,
            SIL.PRODUCT_UOM_ID PRODUCT_UOM,
            SIL.LOCATION_ID,
            SIL.LOCATION_ID LOCATION_DEST_ID,
            'done' STATE,
            'make_to_stock' PROCURE_METHOD,
            TRUE PROPAGATE_CANCEL,
            TRUE IS_INVENTORY,
            'FV:' || SI.NAME REFERENCE,
            SIL.CREATE_UID,
            SI.DATE CREATE_DATE,
            SIL.WRITE_UID,
            SI.DATE WRITE_DATE,
            SI.ID INVENTORY_ID
        FROM
            STOCK_INVENTORY_LINE SIL
            INNER JOIN STOCK_INVENTORY SI ON SIL.INVENTORY_ID = SI.ID
            LEFT JOIN STOCK_MOVE SM ON (
                SIL.INVENTORY_ID = SM.INVENTORY_ID
                AND SIL.PRODUCT_ID = SM.PRODUCT_ID
                AND (
                    SIL.LOCATION_ID = SM.LOCATION_DEST_ID
                    OR SIL.LOCATION_ID = SM.LOCATION_ID
                )
            )
            LEFT JOIN STOCK_MOVE_LINE SML ON (
                SM.ID = SML.MOVE_ID
                AND COALESCE(SIL.PROD_LOT_ID, 0) = COALESCE(SML.LOT_ID, 0)
            )
        WHERE
            SIL.THEORETICAL_QTY = SIL.PRODUCT_QTY
            AND SI.STATE = 'done'
            AND SM.ID IS NULL
    """,
    )


def fill_stock_move_line_zero_inventory(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO
            STOCK_MOVE_LINE (
                MOVE_ID,
                COMPANY_ID,
                PRODUCT_ID,
                PRODUCT_UOM_ID,
                PRODUCT_QTY,
                PRODUCT_UOM_QTY,
                QTY_DONE,
                DATE,
                LOCATION_ID,
                LOCATION_DEST_ID,
                STATE,
                REFERENCE,
                CREATE_UID,
                CREATE_DATE,
                WRITE_UID,
                WRITE_DATE,
                INVENTORY_ADJUSTMENT_ID
            )
        SELECT
            SM.ID MOVE_ID,
            SM.COMPANY_ID,
            SM.PRODUCT_ID,
            SM.PRODUCT_UOM PRODUCT_UOM_ID,
            0 PRODUCT_QTY,
            0 PRODUCT_UOM_QTY,
            0 QTY_DONE,
            SM.DATE,
            SM.LOCATION_ID,
            SM.LOCATION_DEST_ID,
            SM.STATE,
            SM.REFERENCE,
            SM.CREATE_UID,
            SM.CREATE_DATE,
            SM.WRITE_UID,
            SM.WRITE_DATE,
            SM.INVENTORY_ID INVENTORY_ADJUSTMENT_ID
        FROM
            STOCK_INVENTORY_LINE SIL
            INNER JOIN STOCK_INVENTORY SI ON SIL.INVENTORY_ID = SI.ID
            LEFT JOIN STOCK_MOVE SM ON (
                SIL.INVENTORY_ID = SM.INVENTORY_ID
                AND SIL.PRODUCT_ID = SM.PRODUCT_ID
                AND (
                    SIL.LOCATION_ID = SM.LOCATION_DEST_ID
                    OR SIL.LOCATION_ID = SM.LOCATION_ID
                )
            )
            LEFT JOIN STOCK_MOVE_LINE SML ON (
                SM.ID = SML.MOVE_ID
                AND COALESCE(SIL.PROD_LOT_ID, 0) = COALESCE(SML.LOT_ID, 0)
            )
        WHERE
            SIL.THEORETICAL_QTY = SIL.PRODUCT_QTY
            AND SI.STATE = 'done'
            AND SML.ID IS NULL
        """,
    )


def fill_stock_move_line_inventory_quantity(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE STOCK_MOVE_LINE SML
        SET
            INVENTORY_ADJUSTMENT_ID = INVENTORY.INVENTORY_ID,
            PREVIOUS_INVENTORY_QUANTITY = INVENTORY.THEORETICAL_QTY,
            COUNTED_INVENTORY_QUANTITY = INVENTORY.PRODUCT_QTY
        FROM
            (
                SELECT
                    SML.ID SML_ID,
                    SM.INVENTORY_ID,
                    SIL.THEORETICAL_QTY,
                    SIL.PRODUCT_QTY
                FROM
                    STOCK_INVENTORY_LINE SIL
                    INNER JOIN STOCK_INVENTORY SI ON SIL.INVENTORY_ID = SI.ID
                    LEFT JOIN STOCK_MOVE SM ON (
                        SIL.INVENTORY_ID = SM.INVENTORY_ID
                        AND SIL.PRODUCT_ID = SM.PRODUCT_ID
                        AND (
                            SIL.LOCATION_ID = SM.LOCATION_DEST_ID
                            OR SIL.LOCATION_ID = SM.LOCATION_ID
                        )
                    )
                    LEFT JOIN STOCK_MOVE_LINE SML ON (
                        SM.ID = SML.MOVE_ID
                        AND COALESCE(SIL.PROD_LOT_ID, 0) = COALESCE(SML.LOT_ID, 0)
                    )
                WHERE
                    SI.STATE = 'done'
            ) INVENTORY
        WHERE
            SML.ID = INVENTORY.SML_ID
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_move_zero_inventory(env)
    fill_stock_move_line_zero_inventory(env)
    fill_stock_move_line_inventory_quantity(env)
