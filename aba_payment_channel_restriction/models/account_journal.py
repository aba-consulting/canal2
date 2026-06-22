from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    es_canal_2 = fields.Boolean(string="Es canal 2")
