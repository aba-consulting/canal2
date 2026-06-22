from odoo import api, models


class AccountPaymentInvoiceWizardChannel(models.TransientModel):
    _inherit = "account.payment.invoice.wizard"

    @api.depends("payment_id.partner_type")
    def _compute_available_journal_ids(self):
        # Dejar que la implementación base (account_payment_pro) construya el dominio inicial
        super()._compute_available_journal_ids()

        for rec in self:
            journal_type = "sale"
            if rec.payment_id.partner_type == "supplier":
                journal_type = "purchase"

            journal_domain = [
                ("type", "=", journal_type),
                ("company_id", "=", rec.payment_id.company_id.id),
            ]

            # Si el pago tiene líneas a pagar, tomamos el diario de las facturas relacionadas
            # y filtramos por el flag es_canal_2 del diario de la factura.
            invoice_journals = rec.payment_id.to_pay_move_line_ids.mapped("move_id.journal_id")
            if invoice_journals:
                es_canal_2 = bool(invoice_journals[0].es_canal_2)
                if es_canal_2:
                    journal_domain.append(("es_canal_2", "=", True))
                else:
                    journal_domain.append(("es_canal_2", "=", False))

            rec.available_journal_ids = rec.env["account.journal"].search(journal_domain).ids
