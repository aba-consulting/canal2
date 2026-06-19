from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountPaymentChannel(models.Model):
    _inherit = "account.payment"

    available_receiptbook_ids = fields.Many2many(
        "account.payment.receiptbook",
        compute="_compute_available_receiptbook_ids",
        string="Available Receiptbooks",
    )

    @api.depends("company_id", "partner_type", "is_internal_transfer", "journal_id")
    def _compute_available_receiptbook_ids(self):
        for rec in self:
            if rec.is_internal_transfer or not rec.company_id.use_receiptbook:
                rec.available_receiptbook_ids = self.env["account.payment.receiptbook"]
                continue
            partner_type = rec.partner_type or self._context.get(
                "partner_type", self._context.get("default_partner_type", False)
            )
            domain = [
                ("company_id", "child_of", rec.company_id.id),
                ("partner_type", "=", partner_type),
            ]
            if rec.journal_id:
                domain.append(("es_canal_2", "=", rec.journal_id.es_canal_2))
            rec.available_receiptbook_ids = self.env["account.payment.receiptbook"].search(domain)

    @api.depends("company_id", "invoice_ids")
    def _compute_available_journal_ids(self):
        # Primero dejamos que account_payment_pro y account hagan su trabajo
        super()._compute_available_journal_ids()

        for rec in self:
            # Si es una transferencia interna, no aplicamos el filtro de canal
            if rec.is_internal_transfer:
                continue

            # Si no hay diarios disponibles no hacemos nada
            if not rec.available_journal_ids:
                continue

            # Solo filtramos diarios por canal cuando el pago viene vinculado
            # a facturas específicas (invoice_ids).  Las deudas seleccionadas
            # (to_pay_move_line_ids) se auto-cargan y no deben condicionar los
            # diarios disponibles; la consistencia canal/deuda se valida al
            # confirmar mediante el constrains.
            invoice_journals = False
            if rec.invoice_ids:
                invoice_journals = rec.invoice_ids[0].journal_id

            if not invoice_journals:
                continue

            es_canal_2 = bool(invoice_journals[0].es_canal_2)
            if es_canal_2:
                rec.available_journal_ids = rec.available_journal_ids.filtered(lambda j: j.es_canal_2)
            else:
                rec.available_journal_ids = rec.available_journal_ids.filtered(lambda j: not j.es_canal_2)

    @api.depends("company_id", "partner_type", "is_internal_transfer", "journal_id")
    def _compute_receiptbook(self):
        super()._compute_receiptbook()
        for rec in self:
            if rec.is_internal_transfer or not rec.company_id.use_receiptbook:
                continue
            if not rec.journal_id:
                continue
            es_canal_2 = rec.journal_id.es_canal_2
            partner_type = rec.partner_type or self._context.get(
                "partner_type", self._context.get("default_partner_type", False)
            )
            receiptbook = self.env["account.payment.receiptbook"].search(
                [
                    ("partner_type", "=", partner_type),
                    ("company_id", "=", rec.company_id.id),
                    ("es_canal_2", "=", es_canal_2),
                ],
                limit=1,
            )
            rec.receiptbook_id = receiptbook

    @api.constrains("journal_id", "to_pay_move_line_ids", "state")
    def _check_channel_consistency(self):
        for rec in self:
            # Solo validamos la consistencia de canal cuando el pago está siendo
            # confirmado (no en borrador). Esto permite al usuario cambiar el
            # diario, eliminar deudas, etc. sin errores prematuros.
            if rec.state == "draft":
                continue
            if rec.is_internal_transfer or not rec.to_pay_move_line_ids:
                continue
            invoice_journals = rec.to_pay_move_line_ids.mapped("move_id.journal_id")
            if not invoice_journals:
                continue
            deuda_es_canal_2 = any(j.es_canal_2 for j in invoice_journals)
            diario_es_canal_2 = rec.journal_id.es_canal_2
            if deuda_es_canal_2 and not diario_es_canal_2:
                raise UserError(_(
                    "La deuda seleccionada pertenece a Canal 2, "
                    "pero el diario de pago seleccionado no es Canal 2."
                ))
            if not deuda_es_canal_2 and diario_es_canal_2:
                raise UserError(_(
                    "La deuda seleccionada no pertenece a Canal 2, "
                    "pero el diario de pago seleccionado es Canal 2."
                ))