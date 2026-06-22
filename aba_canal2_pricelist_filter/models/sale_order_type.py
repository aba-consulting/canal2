from odoo import fields, models


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    is_canal2 = fields.Boolean(
        string="Es Canal 2",
        default=False,
    )
