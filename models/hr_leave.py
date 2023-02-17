import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

class HRLeave(models.Model):
    _inherit = 'hr.leave'

    def action_validate(self):
        res = super().action_validate()
        for leave in self:
            if leave.state == 'validate':
                _logger.info("validated !")
                for employee in leave.employee_ids:
                    if not leave.request_unit_half and not leave.request_unit_hours:
                        employee._remove_workdays(leave.date_from, leave.date_to)
        return res