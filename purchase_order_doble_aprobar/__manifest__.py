# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Module to generate double approval in purchase orders',
    'version': '1.0',
    'summary': 'Add features to the authorization of a purchase order',
    'license': 'AGPL-3',
    'category': 'Purchase',
    'description': """""",
    'author': 'PROSBOL',
    'website': 'http://www.prosbol.com',
    'depends': ['purchase', 'portal', 'payment', 'base'], #colocar el nombre del modulo que contine las clases a extender
    'description': 'Module for double approval purchase orders',
    'init_xml' : [],
    'demo_xml' : [],
    'data': ["views/purchase_config_settings_views.xml",
             "views/purchase_modifi_cotizacion.xml",
             "views/orden_para_aprobar_template.xml",
             "views/orden_aprobada_template.xml"],
    'active': True,
    'installable': True
}
