from odoo import api, fields, models
import ast
from doc._extensions.pyjsparser.parser import false


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    
    monto_permitido = fields.Integer(sring="Cantidad de dinero permitida sin autorizacion")
    controlar_porcentaje = fields.Boolean(sring="Autorizar porcentajes de descuento")
    enviar_correo = fields.Boolean(sring="Enviar correos de solicitud y respuesta")
    ip_notificacion = fields.Char (string='Ip notificacion', size=16)
    port_notificacion = fields.Char (string='Puerto para notificacion', size=10)
    two_approval = fields.Boolean(sring="Dos aprovaciones")
    users_one_approval = fields.Many2many('res.users', relation='sale_users_one_approval_rel', column1='res_confing_setings_ids', column2='res_user_ids', string='Usuarios primera aprobacion')
    users_two_approval = fields.Many2many('res.users', relation='sale_users_two_approval_rel', column1='res_confing_setings_ids', column2='res_user_ids', string='Usuarios segunda aprobacion')
    @api.model
    def get_values(self): #Para recuperar las variables
        res = super(SaleConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_one_ids = self.env['ir.config_parameter'].sudo().get_param('sale_order_aprobar.users_one_approval')
        user_two_ids = self.env['ir.config_parameter'].sudo().get_param('sale_order_aprobar.users_two_approval')
        if user_one_ids:
            user_one_ids= ast.literal_eval(user_one_ids)
        if user_two_ids:
            user_two_ids=ast.literal_eval(user_two_ids)
        res.update(
            monto_permitido=int(ICPSudo.get_param('sale.monto_permitido', default=int(0))),
            controlar_porcentaje=ICPSudo.get_param('sale.controlar_porcentaje'),
            enviar_correo = ICPSudo.get_param('sale.enviar_correo'),
            ip_notificacion = ICPSudo.get_param('sale.ip_notificacion'),
            port_notificacion = ICPSudo.get_param('sale.port_notificacion'),
            two_approval = ICPSudo.get_param('sale.two_approval'),
            users_one_approval = user_one_ids,
            users_two_approval = user_two_ids,
            )
        return res
    @api.multi
    def set_values(self): #Para guardar las variables
        super(SaleConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("sale.monto_permitido", self.monto_permitido)
        ICPSudo.set_param("sale.controlar_porcentaje", self.controlar_porcentaje)
        ICPSudo.set_param("sale.enviar_correo", self.enviar_correo)
        ICPSudo.set_param("sale.ip_notificacion", self.ip_notificacion)
        ICPSudo.set_param("sale.port_notificacion", self.port_notificacion)
        ICPSudo.set_param("sale.two_approval", self.two_approval)
        ICPSudo.set_param('sale_order_aprobar.users_one_approval', self.users_one_approval.ids)
        ICPSudo.set_param('sale_order_aprobar.users_two_approval', self.users_two_approval.ids)