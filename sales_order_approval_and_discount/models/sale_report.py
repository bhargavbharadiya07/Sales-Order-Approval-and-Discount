from odoo import models, fields

class SaleReport(models.Model):
    _inherit = 'sale.report'

    approval_time = fields.Float(string="Approval Time (Hours)")
    state = fields.Selection(selection_add=[
        ('submitted', 'Submitted for Approval'),
        ('approved_level_1', 'Level 1 Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])
    loyalty_discount = fields.Float(string="Loyalty Discount (%)")
    discounted_amount = fields.Float(string="Discounted Amount")

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res.update({
            'approval_time': "s.approval_time",
            'loyalty_discount': "s.loyalty_discount",
            'discounted_amount': "s.discounted_amount"
        })
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """, s.approval_time, s.loyalty_discount, s.discounted_amount"""
        return res
