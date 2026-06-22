from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    is_canal2 = fields.Boolean(
        string="Es Canal 2",
        default=False,
    )
