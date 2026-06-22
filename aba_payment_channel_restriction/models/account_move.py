from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    available_canal_journal_ids = fields.Many2many(
        "account.journal",
        compute="_compute_available_canal_journal_ids",
        string="Available Canal Journals",
    )

    @api.depends("partner_id", "company_id", "move_type")
    def _compute_sale_type_id(self):
        """Override to preserve existing sale_type_id value"""
        for record in self:
            # Preserve the existing value if it's already set
            existing_value = record.sale_type_id
            # Call parent compute
            super(AccountMove, record)._compute_sale_type_id()
            # If there was an existing value and it's different from what compute set, restore it
            # This allows users to manually select a different sale_type_id (like Canal 2)
            if existing_value and record.sale_type_id != existing_value:
                record.sale_type_id = existing_value

    @api.depends("sale_type_id", "company_id", "suitable_journal_ids", "move_type")
    def _compute_available_canal_journal_ids(self):
        for move in self:
            if move.move_type not in ("out_invoice", "out_refund"):
                move.available_canal_journal_ids = move.suitable_journal_ids
                continue
            base_journals = move.suitable_journal_ids or self.env["account.journal"].search(
                [("company_id", "=", move.company_id.id), ("type", "=", "sale")]
            )
            # Check if sale_type_id name contains "canal 2" (case insensitive)
            is_canal_2 = move.sale_type_id and "canal 2" in (move.sale_type_id.name or "").lower()
            if is_canal_2:
                move.available_canal_journal_ids = base_journals.filtered(lambda j: j.es_canal_2)
            else:
                move.available_canal_journal_ids = base_journals.filtered(lambda j: not j.es_canal_2)

    def _is_canal_2(self):
        return bool(self.sale_type_id and "canal 2" in (self.sale_type_id.name or "").lower())

    def _journal_allowed(self, journal):
        if not journal:
            return True
        if self._is_canal_2():
            return journal.es_canal_2
        return not journal.es_canal_2

    @api.onchange("sale_type_id")
    def _onchange_sale_type_id_journal_domain(self):
        if self.move_type not in ("out_invoice", "out_refund"):
            return
        if self.journal_id and not self._journal_allowed(self.journal_id):
            self.journal_id = False
        return {"domain": {"journal_id": [("id", "in", self.available_canal_journal_ids.ids)]}}

    @api.onchange("journal_id")
    def _onchange_journal_id_check_canal2(self):
        if self.move_type not in ("out_invoice", "out_refund"):
            return
        if self.journal_id and not self._journal_allowed(self.journal_id):
            self.journal_id = False
