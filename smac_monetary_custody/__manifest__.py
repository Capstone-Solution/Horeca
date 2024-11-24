# -*- coding: utf-8 -*-
{
    'name': "Monetary Custody",
    'summary': "Monetary Custody",
    'description': """
        Long description of module's purpose
    """,
    'author': "SMAC",
    'website': "https://www.yourcompany.com",
    'version': '17.0',
    'depends': ['base', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/request_cash_custody.xml',
        'views/reconcile_custody.xml',
        'views/account_move.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
