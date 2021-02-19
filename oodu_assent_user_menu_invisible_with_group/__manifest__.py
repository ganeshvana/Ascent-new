# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'invisble_user_menu_group',
    'version': '1.0',
    'category': 'user',
    'author' : 'Oodu Implementers Private Limited',
    'summary': 'This module for purchase order report',
    'description': """""",
    'website': 'https://www.odooimplementers.com',
    'depends': ['base','web'],
    'data': [],
    'qweb': [
        'static/src/xml/invisible_user_menus.xml',
        
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
}
