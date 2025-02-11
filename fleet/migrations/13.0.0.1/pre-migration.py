# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from openupgradelib import openupgrade

_field_renames = [
    (
        "fleet.vehicle.model.brand",
        "fleet_vehicle_model_brand",
        "image_medium",
        "image_128",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE IR_ATTACHMENT
        SET
            RES_FIELD = 'image_128'
        WHERE
            RES_FIELD = 'image_medium'
            AND RES_MODEL = 'fleet.vehicle.model.brand'
        """,
    )
