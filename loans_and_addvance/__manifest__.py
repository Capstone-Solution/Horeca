# -*- coding: utf-8 -*-
{
    'name': "loans_and_addvance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base', 'hr', 'account', 'hr_payroll', 'employee_analytic_report', 'report_xlsx'],
    'depends': ['base', 'hr', 'account', 'hr_payroll', 'employee_analytic_report', 'mail', 'resignation_request'],
    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/id_sequence.xml',
        'views/views_salary_advance.xml',
        'views/views_pyslib_inh.xml',
        'views/type_loan_advance.xml',
        'views/violations_view.xml',
        'views/violation_category.xml',
        # 'report/loans_and_addvance_report.xml',
        # 'report/advance_report.xml',
        # 'report/report_action_for_excel.xml',
    ],
}
