from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Journal Entry'

    credit_limit_warning = fields.Boolean(compute='_compute_credit_limit_warning')
    allow_credit = fields.Boolean(default=False, copy=False)

    def _compute_credit_limit_warning(self):
        for record in self:
            credit_limit_warning = False
            if record.partner_id and record.partner_id.credit_limit_rules_id and not record.allow_credit:
                invoices = self.env['account.move'].sudo().search([
                    # Facturas y Notas de Crédito
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    # Donde el monto adeudado sea distinto a 0
                    ('amount_residual_signed', '<>', 0.0),
                    # Documento esté publicado
                    ('state', '=', 'posted')])

                if record.partner_id.credit_limit_rules_id.type == 'amount':

                    limite_credito = record.partner_id.credit_limit_rules_id.credit_limit
                    amount_doc = 0.0
                    # Convertirmos el monto a la moneda de la compañía
                    if record.currency_id.id != record.company_id.currency_id.id:
                        amount_doc = 1 / record.currency_rate * record.amount_total
                    else:
                        amount_doc = record.amount_total

                    # Sumo el monto de las facturas
                    for inv in invoices:
                        amount_doc += inv.amount_residual_signed

                    if amount_doc > limite_credito:
                        credit_limit_warning = True
                if record.partner_id.credit_limit_rules_id.type == 'documents':
                    minimo_doc = record.partner_id.credit_limit_rules_id.doc_limit
                    if len(invoices) > minimo_doc:
                        credit_limit_warning = True
            else:
                credit_limit_warning = False
            record.credit_limit_warning = credit_limit_warning

    def action_post(self):
        if self.partner_id and self.partner_id.credit_limit_rules_id and self.move_type in ['out_invoice'] and not self.allow_credit:
            invoices = self.env['account.move'].sudo().search([
                    # Facturas y Notas de Crédito
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    # Donde el monto adeudado sea distinto a 0
                    ('amount_residual_signed', '<>', 0.0),
                    # Documento esté publicado
                    ('state', '=', 'posted')])
                
            if self.partner_id.credit_limit_rules_id.type == 'amount':
                limite_credito = self.partner_id.credit_limit_rules_id.credit_limit
                amount_doc = 0.0
                # Convertirmos el monto a la moneda de la compañía
                if self.currency_id.id != self.company_id.currency_id.id:
                    amount_doc = 1 / self.currency_rate * self.amount_residual_signed
                else:
                    amount_doc = self.amount_residual_signed

                # Sumo el monto de las facturas
                for inv in invoices:
                    amount_doc += inv.amount_residual_signed

                if amount_doc > limite_credito:
                    raise ValidationError(_('The customer has a credit limit rule that is being exceeded by this sales order!'))
            if self.partner_id.credit_limit_rules_id.type == 'documents':
                minimo_doc = self.partner_id.credit_limit_rules_id.doc_limit
                if len(invoices) > minimo_doc:
                    raise ValidationError(_('The partner has a credit limit rule based on the number of unpaid documents!'))
        return super().action_post()

    def action_get_credit_rule_summary(self):
        compose_form = self.env.ref('rn_credit_limit_rules.credit_limit_rule_wizard_view', raise_if_not_found=False).sudo()
        ctx = dict(
            default_partner_id=self.partner_id.id,
            default_account_move_id=self.id,
        )

        return {
            'name': _('Credit Limit Summary'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'credit.limit.rule.wizard',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }