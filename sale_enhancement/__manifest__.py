{
    'name': "Sales General Enhancement",
    'version': '17.0.0.1.0',
    'author': "Zakariya Mahmoud",
    'category': 'Customizations',
    'description': """
    Sales Modules Override
    """,
    'depends': ['base', 'sale', 'product', 'sales_team', 'sale_stock'],
    # data files always loaded at installation
    'data': [
        'reports/report_data.xml',
        'views/product.xml',
        'views/sale.xml'
    ],
    # data files containing optionally loaded demonstration data
    'demo': [],
    'license': 'LGPL-3',
}