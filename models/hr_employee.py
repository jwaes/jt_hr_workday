import logging
from odoo import models, fields, api, exceptions, _
from odoo.tools.date_utils import get_month
from datetime import datetime, timedelta
from pytz import utc
from psycopg2 import IntegrityError


_logger = logging.getLogger(__name__)


def timezone_datetime(time):
    if not time.tzinfo:
        time = time.replace(tzinfo=utc)
    return time




class HrEmployee(models.Model):
    _inherit = "hr.employee"

    preferred_commute_type = fields.Selection([
        ('none', 'None'),
        ('car', 'Car'),
        ('bike', 'Bike'),
    ], string='Commute type', default='none', groups="hr.group_hr_user", help="Default commute type of this employee, can be overruled per workday.")  

    def _is_workingday(self, date):
        self.ensure_one()
        domain = [('company_id', 'in', self.env.company.ids +
                       self.env.context.get('allowed_company_ids', []))]
        from_datetime = datetime.combine(date, datetime.min.time())
        to_datetime = datetime.combine(date, datetime.max.time())
        result = self._get_work_days_data_batch(
            from_datetime, to_datetime, domain=domain)[self.id]
        return result['days'] > 0
    
    def _get_workday(self, date):
        self.ensure_one()
        workday = self.env['jt.hr.workday'].search([
            ('employee_id', '=', self.id),
            ('workday_date', '=', date),
        ])
        return workday

    def _generate_workdays_for_this_month(self):
        today = fields.Date.context_today(self)
        from_date, to_date = get_month(today)
        for employee in self:
            employee._generate_workdays(from_date, to_date)

    def _create_workday(self, date, create_reminder=False):
            for employee in self:
                workday = self.env['jt.hr.workday'].create({
                    'employee_id': employee.id,
                    'workday_date': date,
                    'commute_type' : employee.preferred_commute_type,
                })
                if create_reminder and employee.user_id:
                    workday.activity_schedule(
                        activity_type_id= self._default_activity_type().id,
                        note= "Please review and update workday information.",
                        summary= "Workday information",
                        date_deadline=date,
                        user_id= employee.user_id.id,
                    )

    def _remove_workdays(self, from_date, to_date):
        delta = timedelta(days=1)

        for employee in self:
            iter_date = from_date
            while (iter_date <= to_date):
                workday = employee._get_workday(iter_date)
                if workday:
                    _logger.info("Removing workday %s for employee %s", iter_date, employee)
                    workday.sudo().unlink()
                iter_date += delta                    


    def _generate_workdays(self, from_date, to_date):
        _logger.info("Generating workdays from %s to %s",
                     from_date, to_date)

        delta = timedelta(days=1)

        for employee in self:
            _logger.info("Generating for %s", employee.name)
            iter_date = from_date
            while (iter_date <= to_date):
                if employee._is_workingday(iter_date):
                    if not employee._get_workday(iter_date):
                        try:
                            employee._create_workday(iter_date, create_reminder=True)
                            _logger.info("%s workday created", iter_date)
                        except IntegrityError:
                            _logger.info("try integrityerror")
                    else:
                        _logger.info("%s workday already exists", iter_date)
                else:
                    _logger.info("%s is not a working day", iter_date)
                iter_date += delta
