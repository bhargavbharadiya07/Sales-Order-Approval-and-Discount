from odoo import models, fields

class SaleConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approval_threshold_level_1 = fields.Float(
        string="Level 1 Approval Threshold",
        config_parameter='sale_approval_threshold.level_1',
    )
    approval_threshold_level_2 = fields.Float(
        string="Level 2 Approval Threshold",
        config_parameter='sale_approval_threshold.level_2',
    )

    def set_values(self):
        super(SaleConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'sale_approval_threshold.level_1', self.approval_threshold_level_1)
        self.env['ir.config_parameter'].sudo().set_param(
            'sale_approval_threshold.level_2', self.approval_threshold_level_2)

    def get_values(self):
        res = super(SaleConfigSettings, self).get_values()
        res.update(
            approval_threshold_level_1=float(self.env['ir.config_parameter'].sudo().get_param('sale_approval_threshold.level_1', default=0.0)),
            approval_threshold_level_2=float(self.env['ir.config_parameter'].sudo().get_param('sale_approval_threshold.level_2', default=0.0)),
        )
        return res
