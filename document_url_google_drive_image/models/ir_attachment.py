# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
from base64 import b64encode
from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _get_url(self, url=None):
        url = url or self.url
        url = url.replace("file/d/", "uc?export=view&id=").replace("/view", "")
        url = url.replace("?usp=drive_web", "").replace("?usp=drive_link", "")

        return url

    def _compute_mimetype(self, values):
        if values.get("url") and values.get("type", "url") == "url":
            url = self._get_url(values.get("url"))
            response = requests.get(url.strip())
            content_type = response.headers.get("Content-Type")

            if content_type and content_type.startswith("image/"):
                return content_type

        return super(IrAttachment, self)._compute_mimetype(values)

    def _get_datas(self):
        if self.datas:
            return self.datas
        elif self.url and self.mimetype.startswith("image/"):
            url = self._get_url()
            response = requests.get(url.strip())

            return b64encode(response.content).replace(b"\n", b"")

        return False
