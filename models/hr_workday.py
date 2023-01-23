import logging
from odoo import models, fields, api, _
from odoo.tools.misc import format_date
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime


_logger = logging.getLogger(__name__)


class HrWorkday(models.Model):
    _name = 'jt.hr.workday'
    _description = 'Workday'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'workday_date, employee_id'

    def _default_employee(self):
        return self.env.user.employee_id

    def _default_commute_type(self):
        if self.employee_id:
            return self.employee_id.sudo().preferred_commute_type
        elif self.env.user.employee_id:
            return self.env.user.employee_id.sudo().preferred_commute_type
        else:
            return 'none'

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  default=_default_employee, required=True, ondelete='cascade', index=True)
    workday_date = fields.Date('Date', required=True, tracking=True)

    workday_date_weekday = fields.Char(compute='_compute_workday_date_weekday', string='Weekday')
    
    @api.depends('workday_date')
    def _compute_workday_date_weekday(self):
        for wd in self:
            if wd.workday_date:
                wd.workday_date_weekday = wd.workday_date.strftime('%A')
            else :
                wd.workday_date_weekday = ''

    _sql_constraints = [
        ('employee_workday_unique', 'UNIQUE (employee_id, workday_date)',
         'Workday already exists for this employee')
    ]

    name = fields.Char(compute='_compute_name', string='name')

    @api.depends('employee_id', 'workday_date')
    def _compute_name(self):
        for workday in self:
            workday.name = '%s [%s]' % (
                workday.employee_id.sudo().name, format_date(self.env, workday.workday_date))

    workday_type = fields.Selection([
        ('leave', 'Leave'),
        ('office', 'Office'),
        ('wfh', 'Work from home'),
    ], string='Type', default="office", tracking=True)

    commute_type = fields.Selection([
        ('none', 'None'),
        ('car', 'Car'),
        ('bike', 'Bike'),
    ], string="Commute", default=_default_commute_type, tracking=True)

    @api.onchange('workday_type')
    def _onchange_commute_type(self):
        if self.workday_type != 'office':
            self.commute_type = 'none'

    @api.constrains('workday_type','commute_type')
    def _check_commute(self):
        if self.workday_type == 'office' and self.commute_type == 'none':
            raise ValidationError(_('For a workingday at the office, a commute type other than None must be chosen.'))

    @api.constrains('employee_id', 'workday_date')
    def _check_workday_date(self):
        for workday in self:
            if not workday.employee_id:
                raise ValidationError(_("No employee found."))
            # domain = [('company_id', 'in', self.env.company.ids +
            #            self.env.context.get('allowed_company_ids', []))]
            # from_datetime = datetime.combine(
            #     workday.workday_date, datetime.min.time())
            # to_datetime = datetime.combine(
            #     workday.workday_date, datetime.max.time())
            # result = workday.employee_id._get_work_days_data_batch(
            #     from_datetime, to_datetime, domain=domain)[workday.employee_id.id]
            # # leaveday = workday.employee_id._get_leave_days_data_batch(from_datetime, to_datetime, domain=domain)[workday.employee_id.id]
            # is_workingday = False
            # if result['days'] > 0:
            #     is_workingday = True
            if not workday.employee_id._is_workingday(workday.workday_date):
            # if not is_workingday:
                raise ValidationError(_("This is not a working day."))
