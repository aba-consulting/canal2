from odoo import fields, models


class AccountPaymentReceiptbook(models.Model):
    _inherit = "account.payment.receiptbook"

    es_canal_2 = fields.Boolean(string="Es canal 2")
