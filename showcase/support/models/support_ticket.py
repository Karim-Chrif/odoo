from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SupportTicket(models.Model):
    _name = 'support.ticket'
    _description = 'Support Ticket'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string='Priority', default='medium')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed')
    ], string='State', default='new')
    date_opened = fields.Datetime(string='Date Opened', default=fields.Datetime.now)
    date_closed = fields.Datetime(string='Date Closed')
    assignee_id = fields.Many2one(
        'res.users', 
        string='Assigned To',
        tracking=True,
        domain=[('share', '=', False)]
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure tickets are always created in 'new' state."""
        for vals in vals_list:
            vals['state'] = 'new'
        return super().create(vals_list)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'state' in groupby:
            states = [('new', 'New'), ('in_progress', 'In Progress'), ('closed', 'Closed')]
            result = []
            for state, name in states:
                domain_for_state = [('state', '=', state)]
                count = self.search_count(domain_for_state)
                result.append({
                    'state': state,
                    'state_count': count,
                    '__count': count,
                    '__domain': domain_for_state,
                    '__fold': False,
                    '__can_create': state == 'new'
                })
            return result
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'in_progress' and not self.assignee_id:
            self.assignee_id = self.env.user.id
        elif self.state == 'closed':
            self.date_closed = fields.Datetime.now()

    @api.constrains('state', 'assignee_id')
    def _check_assignee(self):
        for ticket in self:
            if ticket.state == 'in_progress' and not ticket.assignee_id:
                raise ValidationError(_('A ticket in progress must be assigned to someone.'))

    def write(self, vals):
        if vals.get('state') == 'in_progress' and not vals.get('assignee_id') and not self.assignee_id:
            vals['assignee_id'] = self.env.user.id
        return super().write(vals)