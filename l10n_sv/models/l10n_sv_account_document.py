# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models, api


class L10nSvAccountDocument(models.Model):
    _name = "l10n_sv_account.document"
    _description = "Documents"
    _order = "date DESC"

    date = fields.Date(string="Date of Issue", required=True)
    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Description")
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    classification = fields.Selection(
        selection=[("expense", "Expense"), ("cost", "Cost")],
        string="Classification",
        default=False,
    )
    classification_type = fields.Selection(
        selection=[
            ("sales", "Sales"),
            ("admin", "Admin"),
            ("financial", "Financial"),
            ("cost", "Cost"),
        ],
        string="Classification Type",
        default=False,
    )
    l10n_sv_account_document_class_id = fields.Many2one(
        comodel_name="l10n_sv_account.document.class", string="Document Class"
    )
    l10n_sv_account_document_type_id = fields.Many2one(
        comodel_name="l10n_sv_account.document.type", string="Document Type"
    )
    move_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="l10n_sv_account_document_id",
        string="Journal Items",
    )

    def unlink(self):
        for document_id in self:
            for move_line_id in document_id.move_line_ids:
                move_line_id.l10n_sv_account_document_id = False

        return super(L10nSvAccountDocument, self).unlink()

    def name_get(self):
        res = []

        for record in self:
            if record.name:
                name = "%s (%s)" % (record.code or "", record.name or "")
            else:
                name = "%s" % (record.code or "")

            res.append((record.id, name))

        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []

        if name:
            args = ["|", ("code", operator, name), ("name", operator, name)] + args

        return self.search(args, limit=limit).name_get()
