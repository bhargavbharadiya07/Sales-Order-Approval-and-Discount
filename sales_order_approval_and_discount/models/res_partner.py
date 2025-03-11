from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    order_count = fields.Integer(string="Order Count", compute="_compute_loyalty_data", store=True)

    @api.depends('sale_order_ids.amount_total', 'sale_order_ids.state')
    def _compute_loyalty_data(self):
        for partner in self:
            confirmed_orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            order_count = len(confirmed_orders)
            partner.order_count = order_count
