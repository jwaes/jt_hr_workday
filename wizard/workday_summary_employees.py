# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo import api, fields, models
from odoo.tools.date_utils import get_month


class WorkdaySummaryEmployee(models.TransientModel):

    _name = 'jt.hr.workday.summary.employee'
    _description = 'HR Workday Report By Employee'

    def _default_date_from(self):
        today = fields.Date.context_today(self)
        from_date, to_date = get_month(today)
        return from_date

    def _default_date_to(self):
        today = fields.Date.context_today(self)
        from_date, to_date = get_month(today)
        return to_date

    date_from = fields.Date(string='From', required=True, default=_default_date_from)
    date_to = fields.Date(string='To', required=True, default=_default_date_to)
    emp = fields.Many2many('hr.employee', 'workday_emp_rel', 'sum_id', 'emp_id', string='Employee(s)')



    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['emp'] = self.env.context.get('active_ids', [])
        employees = self.env['hr.employee'].browse(data['emp'])
        datas = {
            'ids': [],
            'model': 'hr.employee',
            'form': data
        }
        return self.env.ref('jt_hr_workday.action_report_workdaysummary').report_action(employees, data=datas)
