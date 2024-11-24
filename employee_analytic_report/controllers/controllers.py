# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeAnalyticReport(http.Controller):
#     @http.route('/employee_analytic_report/employee_analytic_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_analytic_report/employee_analytic_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_analytic_report.listing', {
#             'root': '/employee_analytic_report/employee_analytic_report',
#             'objects': http.request.env['employee_analytic_report.employee_analytic_report'].search([]),
#         })

#     @http.route('/employee_analytic_report/employee_analytic_report/objects/<model("employee_analytic_report.employee_analytic_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_analytic_report.object', {
#             'object': obj
#         })
