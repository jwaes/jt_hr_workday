# -*- coding: utf-8 -*-
# from odoo import http


# class JtHrWorkday(http.Controller):
#     @http.route('/jt_hr_workday/jt_hr_workday', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jt_hr_workday/jt_hr_workday/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jt_hr_workday.listing', {
#             'root': '/jt_hr_workday/jt_hr_workday',
#             'objects': http.request.env['jt_hr_workday.jt_hr_workday'].search([]),
#         })

#     @http.route('/jt_hr_workday/jt_hr_workday/objects/<model("jt_hr_workday.jt_hr_workday"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jt_hr_workday.object', {
#             'object': obj
#         })
