# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Module to authorize sales quotes with price and discount greater than normal',
    'version': '1.0',
    'summary': 'Add features to the authorization of a sales order',
    'license': 'AGPL-3',
    'category': 'Sale & order',
    'description': """""",
    'author': 'PROSBOL',
    'website': 'http://www.prosbol.com',
    'depends': ['sale', 'portal', 'payment', 'base'], #colocar el nombre del modulo que contine las clases a extender
    'category' : 'Sale',
    'description': 'Module to approve sales orders',
    'init_xml' : [],
    'demo_xml' : [],
    'data': ["views/sale_config_settings_views.xml",
             #"views/sale_aprobar_venta_views.xml",
             "views/sale_modifi_cotizacion.xml",
             "views/orden_para_aprobar_template.xml",
             "views/orden_aprobada_template.xml"],
    'active': True,
    'installable': True
}
