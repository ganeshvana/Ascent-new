# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Crm Target',
    'category': 'Crm',
    'sequence': 60,
    'summary': 'crm',
    'description': """

    """,
    'website': 'https://www.ooduimplementers.com/',
    'depends': ['crm','base'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_views.xml',
        'views/update_values.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
