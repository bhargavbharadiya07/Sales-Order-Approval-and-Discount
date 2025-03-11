from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('submitted', 'Submitted for Approval'),
        ('approved_level_1', 'Level 1 Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])
    loyalty_discount = fields.Float(string="Loyalty Discount (%)", compute="_compute_loyalty_discount", store=True)
    discounted_amount = fields.Monetary(string="Discounted Amount", compute="_compute_discounted_amount", store=True)
    allow_edit_order = fields.Boolean(string="Can Edit Order", compute="_compute_allow_edit_order", store=False)
    level_1_approval_date = fields.Datetime(string="Level 1 Approval Date")
    level_2_approval_date = fields.Datetime(string="Level 2 Approval Date")
    approval_time = fields.Float(string="Approval Time (Hours)", compute="_compute_approval_time", store=True)

    @api.depends('level_1_approval_date', 'level_2_approval_date')
    def _compute_approval_time(self):
        for order in self:
            if order.level_1_approval_date and order.create_date:
                order.approval_time = (order.level_1_approval_date - order.create_date).total_seconds() / 3600
            elif order.level_2_approval_date and order.level_1_approval_date:
                order.approval_time = (order.level_2_approval_date - order.level_1_approval_date).total_seconds() / 3600
            else:
                order.approval_time = 0.0

    @api.depends('state')
    def _compute_allow_edit_order(self):
        user = self.env.user
        for order in self:
            if order.state in ['submitted', 'approved_level_1']:
                if (order.state == 'submitted' and user.has_group(
                        'sales_order_approval_and_discount.group_order_level_1_approver')) or \
                        (order.state == 'approved_level_1' and user.has_group(
                            'sales_order_approval_and_discount.group_order_level_2_approver')):
                    order.allow_edit_order = True
                else:
                    order.allow_edit_order = False
            else:
                order.allow_edit_order = True

    def _get_approval_threshold(self, level):
        threshold = self.env['ir.config_parameter'].sudo().get_param(f'sale_approval_threshold.{level}', default=0.0)
        return float(threshold)

    def action_submit_for_approval(self):
        self.ensure_one()
        threshold_level_1 = self._get_approval_threshold('level_1')

        if self.amount_total >= threshold_level_1:
            self.state = 'approved'
        else:
            self.state = 'submitted'

    def action_approve_level_1(self):
        if self.state != 'submitted':
            raise UserError("Order must be submitted first.")

        threshold_level_2 = self._get_approval_threshold('level_2')

        if self.amount_total >= threshold_level_2:
            self.state = 'approved'
        else:
            self.state = 'approved_level_1'

        self.write({
            'level_1_approval_date': fields.Datetime.now(),
        })

    def action_approve_level_2(self):
        if self.state != 'approved_level_1':
            raise UserError("Order must be approved at Level 1 first.")

        self.write({
            'state': 'approved',
            'level_2_approval_date': fields.Datetime.now(),
        })

    def action_reject(self):
        self.state = 'rejected'

    @api.depends('amount_total', 'partner_id')
    def _compute_loyalty_discount(self):
        loyalty = self.env['loyalty.discount.rule']
        for order in self:
            if order.partner_id:
                discount = loyalty.get_loyalty_level(order.amount_total,
                                                     order.partner_id.order_count)
                order.loyalty_discount = discount
            else:
                order.loyalty_discount = 0.0
            order._apply_loyalty_discount_to_order_lines()

    @api.depends('amount_total', 'loyalty_discount')
    def _compute_discounted_amount(self):
        for order in self:
            if order.loyalty_discount:
                discount = (order.amount_total * order.loyalty_discount) / 100
                order.discounted_amount = order.amount_total - discount
            else:
                order.discounted_amount = order.amount_total

    @api.onchange('order_line', 'loyalty_discount', 'partner_id')
    def _onchange_partner_discount(self):
        for order in self:
            if order.loyalty_discount:
                order._apply_loyalty_discount_to_order_lines()

    def _apply_loyalty_discount_to_order_lines(self):
        for order in self:
            for line in order.order_line:
                if line.discount != order.loyalty_discount:
                    line.discount = order.loyalty_discount

    def action_open_reject_wizard(self):
        return {
            'name': _("Reject Sale Order"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.reject.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('sales_order_approval_and_discount.sale_order_reject_wizard_form').id,
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }

    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        self.write({'state': 'draft'})
        return res
