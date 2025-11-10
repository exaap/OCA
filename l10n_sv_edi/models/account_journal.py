# Copyright 2024 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    dte_document_type_id = fields.Many2one(
        comodel_name="l10n_sv_account.document.type",
        string="DTE Document Type",
        domain="[('transmission_type', '!=', False)]",
    )
    debitnote_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Debit Note Entry Sequence",
        check_company=True,
        domain="[('company_id', '=', company_id)]",
        help="""This field contains the information related to the numbering of
                the debit note entries of this journal.""",
        copy=False,
    )
    debitnote_sequence = fields.Boolean(
        string="Dedicated Debit Note Sequence",
        help="""Check this box if you don't want to share the same sequence
                for invoices and debit notes made from this journal""",
        default=True,
    )

    @api.constrains("debitnote_sequence_id", "refund_sequence_id", "sequence_id")
    def _check_journal_sequence(self):
        for journal_id in self:
            if (
                journal_id.debitnote_sequence_id
                and journal_id.sequence_id
                and journal_id.debitnote_sequence_id == journal_id.sequence_id
            ):
                raise ValidationError(
                    _(
                        "On journal '%s', the same sequence is used as "
                        "Entry Sequence and Debit Note Entry Sequence.",
                        journal_id.display_name,
                    )
                )

            if (
                journal_id.debitnote_sequence_id
                and journal_id.refund_sequence_id
                and journal_id.debitnote_sequence_id == journal_id.refund_sequence_id
            ):
                raise ValidationError(
                    _(
                        "On journal '%s', the same sequence is used as "
                        "Credit Note Entry Sequence and Debit Note Entry Sequence.",
                        journal_id.display_name,
                    )
                )

            if (
                journal_id.debitnote_sequence_id
                and not journal_id.debitnote_sequence_id.company_id
            ):
                msg = _(
                    "The company is not set on sequence '%(sequence)s' configured as "
                    "debit note sequence of journal '%(journal)s'.",
                    sequence=journal.debitnote_sequence_id.display_name,
                    journal=journal.display_name,
                )
                raise ValidationError(msg)

        super()._check_journal_sequence()
