from odoo import fields, models

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    
    preferred_commute_type = fields.Selection([
        ('none', 'None'),
        ('car', 'Car'),
        ('bike', 'Bike'),
        ], readonly=True, groups="base.group_user")  