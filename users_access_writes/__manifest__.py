{
    'name': "Users Access Writes And Security",
    'version': '17.0.0.1.0',
    'author': "Zakariya Mahmoud",
    'category': 'Customizations',
    'description': """
    groups Security and Access Writes For Modules
    """,
    'depends': ['base', 'sale', 'product', 'crm', 'purchase', 'fleet', 'sales_team', 'mail', 'account', 'calendar',
                'account_reports', 'sale_management', 'stock', 'account_asset', 'account_online_synchronization',
                'account_auto_transfer', 'account_accountant', 'account_disallowed_expenses', 'account_followup',
                'account_online_synchronization', 'sms', 'l10n_be_account_disallowed_expenses_fleet', 'sale_management',
                'barcodes', 'stock_sms', 'stock_account', 'purchase_stock', 'helpdesk'
                ],
    # data files always loaded at installation
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'security/menu.xml',
        'security/report_security.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/stock_picking.xml',
        'views/crm.xml',
        'views/purchase.xml',
        'views/desk_partner.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [],
    'license': 'LGPL-3',
}
