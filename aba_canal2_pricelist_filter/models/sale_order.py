from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_canal_2_type = fields.Boolean(
        string="Es tipo Canal 2",
        compute="_compute_is_canal_2_type",
        store=False,
    )

    @api.depends('type_id', 'type_id.is_canal2')
    def _compute_is_canal_2_type(self):
        for order in self:
            order.is_canal_2_type = bool(
                order.type_id and order.type_id.is_canal2
            )

    @api.onchange('type_id')
    def _onchange_type_id_clear_pricelist_canal2(self):
        """Limpia la lista de precios si no coincide con el tipo Canal 2"""
        if self.type_id and self.pricelist_id:
            is_canal_2_type = self.type_id.is_canal2
            is_canal_2_pricelist = self.pricelist_id.is_canal2

            # Si el tipo es Canal 2 pero la lista no lo es, limpiar
            if is_canal_2_type and not is_canal_2_pricelist:
                self.pricelist_id = False
            # Si el tipo NO es Canal 2 pero la lista sí lo es, limpiar
            elif not is_canal_2_type and is_canal_2_pricelist:
                self.pricelist_id = False
