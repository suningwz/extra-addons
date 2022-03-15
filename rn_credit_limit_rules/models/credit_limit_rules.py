from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class CreditLimitRule(models.Model):
    _name = "credit.limit.rule"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Credit Limit Rule"

    name   = fields.Char(string="Credit Limit Rules Name", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    type = fields.Selection([
        ('amount', 'Amount'),
        ('documents', 'Documents')
    ], string='Credit Rule Type', default='amount')

    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 store=True, readonly=True,
                                 default=lambda self: self.env.user.company_id )
    currency_id = fields.Many2one(string='Currency', readonly=True,
        related='company_id.currency_id')

    credit_limit = fields.Monetary(string='Amount Credit Limit', store=True)
    doc_limit = fields.Integer(string='Document Limit')

    active = fields.Boolean(default=True, help="Set active to false to hide the rule without removing it.")


    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            seq_date = fields.Datetime.now()
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.limit.rule', sequence_date=seq_date) or _('New')

        return super().create(vals)