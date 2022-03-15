from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Journal Entry'

    credit_limit_warning = fields.Boolean(compute='_compute_credit_limit_warning')

    def _compute_credit_limit_warning(self):
        for record in self:
            credit_limit_warning = False
            if record.partner_id:
                rules = record.partner_id.credit_limit_rules_ids
                if rules:
                    limite = []
                    overdue_docs = []
                    invoices = self.env['account.move'].sudo().search([
                        # Facturas y Notas de Crédito
                        ('move_type', 'in', ['out_invoice', 'out_refund']),
                        # Donde el monto adeudado sea distinto a 0
                        ('amount_residual_signed', '<>', 0.0),
                        # Documento esté publicado
                        ('state', '=', 'posted')])
                    for rule in rules:
                        if rule.type == 'amount':
                            limite.append(rule.credit_limit)
                        if rule.type == 'documents':
                            overdue_docs.append(rule.doc_limit)
                    if len(overdue_docs) > 0:
                        overdue_docs.sort()
                        minimo_doc = overdue_docs[0]
                        if len(invoices) > minimo_doc:
                            credit_limit_warning = True
                    if len(limite) > 0:
                        limite.sort()
                        limite_credito = limite[0]
                        amount_doc = self.amount_residual_signed

                        # Sumo el monto de las facturas
                        for inv in invoices:
                            amount_doc += inv.amount_residual_signed

                        if amount_doc > limite_credito:
                            credit_limit_warning = True
                else:
                    credit_limit_warning = False
            else:
                credit_limit_warning = False
            record.credit_limit_warning = credit_limit_warning

    def action_post(self):
        if self.partner_id and self.move_type in ['out_invoice']:
            rules = self.partner_id.credit_limit_rules_ids
            if rules:
                limite = []
                overdue_docs = []
                invoices = self.env['account.move'].sudo().search([
                        # Facturas y Notas de Crédito
                        ('move_type', 'in', ['out_invoice', 'out_refund']),
                        # Donde el monto adeudado sea distinto a 0
                        ('amount_residual_signed', '<>', 0.0),
                        # Documento esté publicado
                        ('state', '=', 'posted')])
                for rule in rules:
                    if rule.type == 'amount':
                        limite.append(rule.credit_limit)
                    if rule.type == 'documents':
                        overdue_docs.append(rule.doc_limit)
                if len(overdue_docs) > 0:
                    overdue_docs.sort()
                    minimo_doc = overdue_docs[0]
                    if len(invoices) > minimo_doc:
                        raise ValidationError(_('The partner has a credit limit rule based on the number of unpaid documents!'))
                    return super().action_post()
                if len(limite) > 0:
                    limite.sort()
                    limite_credito = limite[0]
                    amount_doc = self.amount_residual_signed

                    # Sumo el monto de las facturas
                    for inv in invoices:
                        amount_doc += inv.amount_residual_signed

                    if amount_doc > limite_credito:
                        raise ValidationError(_('The customer has a credit limit rule that is being exceeded by this document!'))
        return super().action_post()