from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrderRejectWizard(models.TransientModel):
    _name = 'sale.order.reject.wizard'
    _description = 'Reject Sale Order'

    reason = fields.Text(string="Rejection Reason", required=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    def action_reject_order(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError("No sale order linked!")

        self.sale_order_id.state = 'rejected'

        self.sale_order_id.message_post(body=f"<b>Order Rejected :-</b> {self.reason}")

        return {'type': 'ir.actions.act_window_close'}
