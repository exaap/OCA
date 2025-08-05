# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def binary_content(
        cls,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        unique=False,
        filename=None,
        filename_field="datas_fname",
        download=False,
        mimetype=None,
        default_mimetype="application/octet-stream",
        access_token=None,
        related_id=None,
        access_mode=None,
        env=None,
    ):
        status, headers, content = super(IrHttp, cls).binary_content(
            xmlid=xmlid,
            model=model,
            id=id,
            field=field,
            unique=unique,
            filename=filename,
            filename_field=filename_field,
            download=download,
            mimetype=mimetype,
            default_mimetype=default_mimetype,
            access_token=access_token,
            related_id=related_id,
            access_mode=access_mode,
            env=env,
        )

        if status == 301 and model == "ir.attachment" and id:
            attachment_id = env[model].sudo().browse(id)

            if (
                attachment_id
                and attachment_id.url
                and attachment_id.mimetype.startswith("image/")
            ):
                return 200, headers, attachment_id._get_datas() or content

        return (status, headers, content)
