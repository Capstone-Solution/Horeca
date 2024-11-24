{
    'name': "Inventory General Enhancement",
    'version': '17.0.0.1.0',
    'author': "Zakariya Mahmoud",
    'category': 'Customizations',
    'description': """
    Inventory Modules Override
    """,
    'depends': ['base', 'stock'],
    # data files always loaded at installation
    'data': [
        'views/stock_picking_type.xml'
    ],
    # data files containing optionally loaded demonstration data
    'demo': [],
    'license': 'LGPL-3',
}
