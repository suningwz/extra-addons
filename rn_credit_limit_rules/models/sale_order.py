from odoo import models, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_limit_warning = fields.Boolean(compute='_compute_credit_limit_warning')
    allow_credit = fields.Boolean(default=False, copy=False)

    def _compute_credit_limit_warning(self):
        for record in self:
            credit_limit_warning = False
            if record.partner_id and record.partner_id.credit_limit_rules_id and not record.allow_credit:
                invoices = self.env['account.move'].sudo().search([('move_type', 'in', ['out_invoice', 'out_refund']),
                                                                   ('amount_residual_signed', '<>', 0.0),
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

    def action_confirm(self):
        for record in self:
            if record.partner_id and record.partner_id.credit_limit_rules_id and not record.allow_credit:

                invoices = self.env['account.move'].sudo().search([('move_type', 'in', ['out_invoice', 'out_refund']),
                                                                   ('amount_residual_signed', '<>', 0.0),
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
                        raise ValidationError(_('The customer has a credit limit rule that is '
                                                'being exceeded by this sales order!'))
                if record.partner_id.credit_limit_rules_id.type == 'documents':
                    minimo_doc = record.partner_id.credit_limit_rules_id.doc_limit
                    if len(invoices) > minimo_doc:
                        raise ValidationError(_('The partner has a credit limit rule based on '
                                                'the number of unpaid documents!'))

            return super().action_confirm()

    def action_get_credit_rule_summary(self):
        compose_form = self.env.ref('rn_credit_limit_rules.credit_limit_rule_wizard_view',
                                    raise_if_not_found=False).sudo()
        ctx = dict(default_partner_id=self.partner_id.id, default_sale_order_id=self.id)

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

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res['allow_credit'] = self.allow_credit
        return res
