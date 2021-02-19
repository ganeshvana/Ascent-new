# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Restrict Change Sales Team",
    "version" : "13.0",
    "category" : "crm",
    'summary': 'Restrict to change sales team to the user in crm lead',
    "depends" : ['crm'],
    "data": [
        'security/crm_security.xml',
        'views/crm_view.xml',
    ],
    "auto_install": False,
    "installable": True,
}
