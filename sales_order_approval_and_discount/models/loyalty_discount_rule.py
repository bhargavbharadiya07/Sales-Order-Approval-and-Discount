from odoo import api, models, fields

class LoyaltyDiscountRule(models.Model):
    _name = 'loyalty.discount.rule'
    _description = 'Loyalty Discount Rule'

    name = fields.Char(string="Loyalty Level", required=True)
    min_purchase = fields.Float(string="Min Purchase Amount", required=True)
    min_orders = fields.Integer(string="Min Orders", required=True)
    discount_percentage = fields.Float(string="Discount (%)", required=True)

    @api.model
    def get_loyalty_level(self, total_purchase, order_count):
        loyalty_level = self.env['loyalty.discount.rule'].search([], order="min_purchase desc, min_orders desc")
        for level in loyalty_level:
            if total_purchase >= level.min_purchase and order_count >= level.min_orders:
                return level.discount_percentage
        return 0.0