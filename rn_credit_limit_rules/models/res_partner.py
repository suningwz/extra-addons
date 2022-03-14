
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class PartnerCreditLimit(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner Credit Limit'

    credit_limit_rules_ids = fields.Many2many('credit.limit.rule', 'rule_partner_rel', 'partner_id', 'rule_id', string='Credit Limit Rules')

    @api.onchange('parent_id')
    def _onchange_parent_id_for_credit_limit(self):
        if self.parent_id and self.parent_id.credit_limit_rules_ids:
            self.credit_limit_rules_ids = self.parent_id.credit_limit_rules_ids.ids