from odoo import api, fields, models
import ast


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    
    two_approval_purchase = fields.Boolean(sring="Dos aprovaciones")
    users_one_approval_purchase = fields.Many2many('res.users', relation='purchase_users_one_approval_rel', column1='res_confing_setings_ids', column2='res_user_ids', string='Usuarios primera aprobacion')
    users_two_approval_purchase = fields.Many2many('res.users', relation='purchase_users_two_approval_rel', column1='res_confing_setings_ids', column2='res_user_ids', string='Usuarios segunda aprobacion')
    @api.model
    def get_values(self): #Para recuperar las variables
        res = super(SaleConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_one_ids = self.env['ir.config_parameter'].sudo().get_param('purchase.users_one_approval_purchase')
        user_two_ids = self.env['ir.config_parameter'].sudo().get_param('purchase.users_two_approval_purchase')
        if user_one_ids:
            user_one_ids= ast.literal_eval(user_one_ids)
        if user_two_ids:
            user_two_ids=ast.literal_eval(user_two_ids)
        res.update(
            two_approval_purchase = ICPSudo.get_param('purchase.two_approval_purchase'),
            users_one_approval_purchase = user_one_ids,
            users_two_approval_purchase = user_two_ids,
            )
        return res
    @api.multi
    def set_values(self): #Para guardar las variables
        super(SaleConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("purchase.two_approval_purchase", self.two_approval_purchase)
        ICPSudo.set_param('purchase.users_one_approval_purchase', self.users_one_approval_purchase.ids)
        ICPSudo.set_param('purchase.users_two_approval_purchase', self.users_two_approval_purchase.ids)