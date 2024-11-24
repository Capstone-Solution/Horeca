{
    'name': 'Sale Order Horeca Integration',
    'version': '1.0',
    'summary': 'Send a POST request to Horeca server on sale order confirmation',
    'description': 'This module sends a POST request to Horeca server with user_id, total, odoo_reference, discount, notes, and order line details when a sale order is confirmed.',
    'author': 'M.Rageh',
    'depends': ['sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
}
