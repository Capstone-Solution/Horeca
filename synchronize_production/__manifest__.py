# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'synchronize',
    'version': '17.0.1.0.0',
    'summary': 'Synchronize screen',
    'description': 'Synchronize screen',
    'author': 'Hossam Hassan',
    'license': 'LGPL-3',
    'depends': ['base', 'stock','contact_leads'],
     'images': [
        'static/src/img/default_image.png',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/sync_views.xml',
        'data/data.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 5,
    'auto_install': False,
}
