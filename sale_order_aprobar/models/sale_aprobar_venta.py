# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp, ast
from doc._extensions.pyjsparser.parser import false

class sale_order(models.Model):
    _inherit = "sale.order"
    aprobar_monto = fields.Integer("Cantidad de dinero permitida sin autorizacion")
    aprobar_sale = fields.Boolean("Aprobar orden de venta")
    state = fields.Selection(selection_add=[('to approve', 'Para aprobar'), ('approve', 'Aprobado'), ('two_to_approve', 'Esperando Segunda aprobacion')])
    ajuste_descuento= fields.Monetary(compute = "_ajuste_descuento")
    ajuste_descuento_line= fields.Char(compute = "_ajuste_descuento_line")
    precio_total= fields.Float(string='Precio total sin descuento e impuestos', compute = "_precio_total")
    descuento_total = fields.Float(string='Descuento total (%)', digits=dp.get_precision('Discount'), default=0.0)
    sindesc_total = fields.Float(string='Precio total sin descuento e impuestos')
    
    @api.onchange('descuento_total')
    def _ajuste_descuento(self):
        """
        Compute the total amounts of the SO.aprobar_monto_get != 0
        """
        if self.descuento_total > -1:
            for order in self: 
                for line in order.order_line:      
                    if line.discount!= self.descuento_total:
                        line.discount = self.descuento_total
                        line.price_subtotal = 0
                    line._compute_amount() 
        if self.descuento_total > -1:
            for order in self:
                for line in order.order_line:      
                    if line.discount!= self.descuento_total:
                        if self.descuento_total!=0:
                            line.discount = self.descuento_total
                        line.price_subtotal = 0
                    line._compute_amount()             
        return

    @api.depends('order_line.discount', 'order_line.product_id', 'order_line.product_uom_qty', 'order_line.price_unit', 'order_line.tax_id')
    def _ajuste_descuento_line(self):
        """
        Compute the total amounts of the SO.
        """
        precio_t = 0
        descuento_unit = self.descuento_total
        if self.descuento_total > -1:
            for order in self:
                for line in order.order_line:   
                    if line.discount!= self.descuento_total:
                        self.descuento_total = 0
        self._amount_all()
        precio_t = self._t_calc_total()
        self.sudo().write({'sindesc_total':precio_t})
        self.precio_total=precio_t       
        return
    def _t_calc_total(self):
        precio = 0
        for order in self:
            for line in order.order_line:
                precio = precio + line.price_unit*line.product_uom_qty
        return precio

    @api.onchange('descuento_total')
    def _precio_total(self):
        for order in self:
            precio_t = order._t_calc_total()
            order.sudo().write({'sindesc_total':precio_t})
            order.sindesc_total=precio_t
            order.precio_total=precio_t
        return
    @api.one
    def action_confirm(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        aprobar_monto_get = int(ICPSudo.get_param('sale.monto_permitido', default=int(0)))
        controlar_porcentaje_get=ICPSudo.get_param('sale.controlar_porcentaje')           
        enviar_correo_get = ICPSudo.get_param('sale.enviar_correo') 
        two_approval = ICPSudo.get_param('sale.two_approval')
        if not two_approval:  
            if aprobar_monto_get != 0 and aprobar_monto_get != None:
                if aprobar_monto_get < self.amount_total:
                    if self.env['res.users'].has_group('sales_team.group_sale_manager'):
                        if self.state == "draft":
                            self.write({'state': 'to approve'})
                            if enviar_correo_get==True:
                                users_send = self.env['res.users'].has_group('sales_team.group_sale_manager')
                                self.send_mail(users_send, "manager")
                            return
                        if self.state == "to approve":
                            raise UserError(_("No tiene permiso para aprobar esta orden de venta"))
                    if self.env['res.users'].has_group('sales_team.group_sale_manager'):
                        self.aprobar_sale = True
            if controlar_porcentaje_get == True:
                tiene_desuento = ""
                for selfie in self.order_line:
                    if selfie.discount > 0:
                        tiene_desuento = "Si"
                        break
                if tiene_desuento =="Si":
                    if not self.env['res.users'].has_group('sales_team.group_sale_manager'):
                            if self.state == "draft":
                                self.write({'state': 'to approve'})
                                if enviar_correo_get==True:
                                    result = self._cr.execute("""SELECT res_groups_users_rel.uid FROM 
                                                                    public.ir_model_data, 
                                                                    public.res_groups_users_rel
                                                                WHERE 
                                                                    ir_model_data.res_id = res_groups_users_rel.gid AND
                                                                    ir_model_data.name = 'group_sale_manager';""")
                                    result = self._cr.dictfetchall()
                                    try:
                                        self.send_mail(result, "manager")
                                    except:
                                        raise UserError(_("El servidor de correos tiene problemas intente mas tarde o comuniquese con el administardor"))             
                                return
                            if self.state == "to approve":
                                raise UserError(_("No tiene permiso para aprobar esta orden de venta"))    
                    if self.env['res.users'].has_group('sales_team.group_sale_manager'):
                        self.aprobar_sale = True
                        self.state = 'approve'
                        if enviar_correo_get==True:
                            try:
                                self.send_mail(self.env.user, "respuesta_aprove")
                            except:
                                raise UserError(_("El servidor de correos tiene problemas intente mas tarde o comuniquese con el administardor"))     
        if two_approval:
            user_one_ids = ast.literal_eval(ICPSudo.get_param('sale_order_aprobar.users_one_approval'))
            user_two_ids = ast.literal_eval(ICPSudo.sudo().get_param('sale_order_aprobar.users_two_approval'))
            user_one_id = False
            user_two_id = False
            user_one_id=[user_one_id for user_one_id in user_one_ids if user_one_id==self._context['uid']]
            user_two_id=[user_two_id for user_two_id in user_two_ids if user_two_id==self._context['uid']]
            if (aprobar_monto_get != 0 and aprobar_monto_get != None) or controlar_porcentaje_get == True:
                tiene_desuento = ""
                for selfie in self.order_line:
                    if selfie.discount > 0:
                        tiene_desuento = "Si"
                        break
                if tiene_desuento =="Si" or aprobar_monto_get != 0:
                    if not user_one_id and not user_two_id:
                        if self.state == "draft":
                            self.write({'state': 'to approve'})
                            if enviar_correo_get==True:
                                result = self._cr.execute("""SELECT res_groups_users_rel.uid FROM 
                                                                public.ir_model_data, 
                                                                public.res_groups_users_rel
                                                            WHERE 
                                                                ir_model_data.res_id = res_groups_users_rel.gid AND
                                                                ir_model_data.name = 'group_sale_manager';""")
                                result = self._cr.dictfetchall()
                                try:
                                    self.send_mail(result, "manager")
                                except:
                                    raise UserError(_("El servidor de correos tiene problemas intente mas tarde o comuniquese con el administardor"))             
                            return False
                        if self.state == "to approve":
                            raise UserError(_("No tiene permiso para aprobar esta orden de venta"))
                        if self.state == "two_to_approve":
                            raise UserError(_("No tiene permiso para aprobar esta orden de venta esperando la segunda aprobacion"))  
                    if user_one_id:
                        if self.state!='two_to_approve':
                            self.aprobar_sale = False
                            self.write({'state': 'two_to_approve'})
                            if enviar_correo_get==True:
                                try:
                                    self.send_mail(self.env.user, "respuesta_aprove")
                                except:
                                    raise UserError(_("El servidor de correos tiene problemas intente mas tarde o comuniquese con el administardor"))
                            if not user_two_id:
                                self.aprobar_sale = False
                                return False
#                                 raise UserError(_("No tiene permiso para aprobar esta orden de venta esperando la segunda aprobacion"))  
                        else:
                            if not user_two_id:
                                raise UserError(_("No tiene permiso para aprobar esta orden de venta esperando la segunda aprobacion"))  
                    if user_two_id:
                        if self.state!='two_to_approve':
                            raise UserError(_("No tiene permiso para aprobar esta orden de venta esperando la primera aprobacion"))  
                        self.aprobar_sale = True
                        self.state = 'approve'
                        if enviar_correo_get==True:
                            try:
                                self.send_mail(self.env.user, "respuesta_aprove")
                            except:
                                raise UserError(_("El servidor de correos tiene problemas intente mas tarde o comuniquese con el administardor"))      
        return super(sale_order, self).action_confirm() #RETORNA A LA FUNCION PADRE
    @api.one
    def action_desbloqueo(self):
        if self.state == "done" and self.invoice_status!="to invocie":
            self.write({'state': 'sale'})
            self.write({'aprobar_sale': False})
            return
    @api.one
    def action_desbloqueo_approve(self):
        if self.state == 'sale':
            status = self._verifica_out_vs_in_stockmoves()
            if status=='cancell':
                self.write({'aprobar_sale': False,
                            'state':'to approve'})
            if status=='nocancell':
                raise UserError(_("No puede revertir una orden aprobada y que tiene movimientos de almacen no revertidos")) 
#     @api.multi
#     def write(self, vals):
#         if 'sindesc_total' in vals:
#             self.sindesc_total = vals['sindesc_total']
#         return super(sale_order, self).write(vals) #RETORNA A LA FUNCION PADRE
    @api.one
    def send_mail(self, users_send, type_send):
        rendering_context = {} #variable que llevara las variables al template del mail
        send_mails = ""
        if type_send=="manager": #Verifica si el correo a enviar es para solicitar aprobar la orden 
            template = self.env.ref('sale_order_aprobar.orden_para_aprobar') #template que tiene el html del mail
            for user_send in users_send:
                id_s = user_send['uid']
                u_send = self.env['res.users'].search([('id','=',id_s)])
                if u_send.email != False:
                    send_mails = send_mails + u_send.email +";"
            rendering_context.update({
                'lang': self.user_id.lang,
                'user_name': self.user_id.name,
                'user_mail': self.user_id.email,
                'correos_enviar': send_mails,
                'base_url': self.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069')+"/web?#id="+str(self.id)+"&view_type=form&model=sale.order&action=243"
            })                
            template.with_context(rendering_context).send_mail(self.user_id.id, force_send=True, raise_exception=True) 
        if type_send=="respuesta_aprove": #Verifica si el correo a enviar es con la orden aprobada 
            template = self.env.ref('sale_order_aprobar.orden_aprobada')
            rendering_context.update({
                'lang': self.user_id.lang,
                'user_name': users_send.name,
                'user_mail': users_send.email,
                'correos_enviar': self.user_id.email,
                'base_url': self.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069')+"/web?#id="+str(self.id)+"&view_type=form&model=sale.order&action=243"
            })                
            template.with_context(rendering_context).send_mail(self.user_id.id, force_send=True, raise_exception=True) 
        #self.env['mail.template'].browse(template.id).send_mail(self.id)

 
class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    ajuste_descuento_line= fields.Char(compute = "_ajuste_descuento_order_line")
    ajuste_descuento_line_to= fields.Char(compute = "_ajuste_descuento_order_line_to")
    @api.onchange('discount')
    def _ajuste_descuento_order_line(self):
        """
        Compute the total amounts of the SO.
        """
        if len(self) < 2:
            if self.order_id.descuento_total > -1:
                self.discont = self.order_id.descuento_total
        else:
            for selfies in self:
                if selfies.order_id.descuento_total > -1:
                    selfies.discont = selfies.order_id.descuento_total
        return
    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if self.order_id.descuento_total > -1:
            self.discount = self.order_id.descuento_total

        else:
            self.discount = 0.0 
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return
        else:
            return super(sale_order_line, self)._onchange_discount() #RETORNA A LA FUNCION PADRE                   
    @api.depends('price_total')
    def _ajuste_descuento_order_line_to(self):
        self.order_id.sindesc_total = 9  
        return  