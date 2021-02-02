# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp, ast

class purchase_order(models.Model):
    _inherit = "purchase.order"
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approve', 'Primera aprobacion'), ('two_to_approve', 'Segunda aprobacion'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    two_approval_purchase = fields.Boolean(compute="_compute_two_approval")
    def _compute_two_approval(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        two_purchase = ICPSudo.get_param('purchase.two_approval_purchase')
        self.two_approval_purchase = two_purchase
        
    @api.multi
    def button_confirm(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        two_approval_purchase = ICPSudo.get_param('purchase.two_approval_purchase')
        if not two_approval_purchase:
            for order in self:
                if order.state not in ['draft', 'sent']:
                    continue
                order._add_supplier_to_product()
                # Deal with double validation process
                if order.company_id.po_double_validation == 'one_step'\
                        or (order.company_id.po_double_validation == 'two_step'\
                            and order.amount_total < self.env.user.company_id.currency_id._convert(
                                order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                        or order.user_has_groups('purchase.group_purchase_manager'):
                    order.button_approve()
                else:
                    order.write({'state': 'to approve'})
            return True
        if two_approval_purchase:
            user_one_ids = ast.literal_eval(ICPSudo.get_param('purchase.users_one_approval_purchase'))
            user_two_ids = ast.literal_eval(ICPSudo.sudo().get_param('purchase.users_two_approval_purchase'))
            user_one_id = False
            user_two_id = False
            user_one_id=[user_one_id for user_one_id in user_one_ids if user_one_id==self._context['uid']]
            user_two_id=[user_two_id for user_two_id in user_two_ids if user_two_id==self._context['uid']]
            for order in self:
                if order.company_id.po_double_validation_amount < order.amount_total:
                    if not user_one_id and not user_two_id:
                        if order.state == "draft":
                            order.write({'state': 'to approve'})
                            return False
                        if order.state == "to approve":
                            raise UserError(_("No tiene permiso para aprobar esta orden de compra"))
                        if order.state == "two_to_approve":
                            raise UserError(_("No tiene permiso para aprobar esta orden de compra esperando la segunda aprobacion"))  
                    if user_one_id:
                        if order.state!='two_to_approve':
                            order.write({'state': 'two_to_approve'})
                            if not user_two_id:
                                order.aprobar_sale = False
                                return False
                        else:
                            if not user_two_id:
                                raise UserError(_("No tiene permiso para aprobar esta orden de compra esperando la segunda aprobacion"))  
                    if user_two_id:
                        if order.state!='two_to_approve':
                            raise UserError(_("No tiene permiso para aprobar esta orden de compra esperando la primera aprobacion"))  
                        order.state = 'approve'
                        order.button_approve()
                else:
                    order.button_approve()
