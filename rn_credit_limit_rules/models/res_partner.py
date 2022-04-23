
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class PartnerCreditLimit(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner Credit Limit'

    credit_limit_rules_id = fields.Many2one('credit.limit.rule', string='Credit Limit Rules')

    @api.onchange('parent_id')
    def _onchange_parent_id_for_credit_limit(self):
        if self.parent_id and self.parent_id.credit_limit_rules_id:
            self.credit_limit_rules_id = self.parent_id.credit_limit_rules_id.id