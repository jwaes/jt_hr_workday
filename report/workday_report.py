import calendar
import logging

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HrEmployeeWorkdayReport(models.AbstractModel):
    _name = 'report.jt_hr_workday.report_workdaysummary'
    _description = 'Employee Workday Summary Report'

    def _get_header_info(self, start_date, end_date):
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        return {
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
        }

    def _get_data_from_report(self, data):
        res = []
        Employee = self.env['hr.employee']
        if 'emp' in data:
            res.append({'data': [
                self._get_workdays_summary(data['date_from'], data['date_to'], emp.id)
                for emp in Employee.browse(data['emp'])
            ]})
        return res

    def _get_workdays_summary(self, start_date, end_date, empid):

        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        
        employee = self.env['hr.employee'].browse(empid)

        workdays = employee._get_workdays_between(start_date, end_date)

        data = {
            'name': employee.name,
        }

        delta = timedelta(days=1)
        iter_date = start_date

        workday_days_sum = 0
        workday_type_sum = {}
        workday_commute_sum = {}
        workday_leave_sum = {}

        data['days'] = []
        while (iter_date <= end_date):
            workday = employee._get_workday(iter_date)
            details = employee._get_workingday_details(iter_date)
            iter_date_start = datetime.combine(iter_date, datetime.min.time())
            iter_date_end = datetime.combine(iter_date, datetime.max.time())            

            holidays = self.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee.id),
                ('date_from', '<=', iter_date),
                ('date_to', '>=', iter_date),
                ('state', '=', 'validate')
            ])

            dayinfo = {
                'date' : iter_date,
                'days' : details['days'],
                'hours': details['hours'],
                'type': workday.workday_type_name,
                'commute_type' : workday.commute_type_name,
                'leave' : False,
            }            

            if details['days'] > 0:
                workday_days_sum += 1


            if workday.workday_type and workday.workday_type != 'leave':                
                type_count = 0
                type_name = workday.workday_type_name

                if type_name in workday_type_sum:
                    type_count = workday_type_sum[type_name]
                type_count += 1
                workday_type_sum[type_name] = type_count


            if workday.commute_type and workday.commute_type != 'none':                
                type_count = 0
                type_name = workday.commute_type_name

                if type_name in workday_commute_sum:
                    type_count = workday_commute_sum[type_name]
                type_count += 1
                workday_commute_sum[type_name] = type_count



            if holidays:
                if len(holidays) > 1:
                    raise UserError("more than 1 holiday on this day ??")
                type_name = holidays[0].holiday_status_id.display_name
                dayinfo['leave'] = True
                dayinfo['leave_type'] = type_name
                dayinfo['leave_days'] = holidays[0].number_of_days
                dayinfo['leave_hours'] = holidays[0].number_of_hours_display

                type_count = 0.0
                if type_name in workday_leave_sum:
                    type_count = workday_leave_sum[type_name]
                if holidays[0].number_of_days > 1:
                    type_count += 1
                else :
                    type_count += holidays[0].number_of_days
                workday_leave_sum[type_name] = type_count

            data['days'].append(dayinfo)
            iter_date += delta    

        data['workday_days_sum'] = workday_days_sum
        data['workday_type_sum'] = workday_type_sum
        data['workday_commute_sum'] = workday_commute_sum
        data['workday_leave_sum'] = workday_leave_sum

        # data['workdays'] = [
        #     self._get_workday_data(workday)
        #     for workday in workdays

        # ]

        return data

    def _get_workday_data(self, workday):
        data = {
            'date' : workday.workday_date,
            'weekday' : workday.workday_date_weekday,
            'name': workday.name,
            'type': workday.workday_type,
            'type' : workday.commute_type,
        }
        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        workdays_report = self.env['ir.actions.report']._get_report_from_name('jt_hr_workday.report_workdaysummary')

        res = {
            'doc_ids': self.ids,
            'doc_model': workdays_report.model,        
            'get_header_info': self._get_header_info(data['form']['date_from'],data['form']['date_to']),
            'get_data_from_report': self._get_data_from_report(data['form']),            
        }

        return res