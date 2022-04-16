from odoo import api, fields, models

class ReSequenceWizard(models.TransientModel):
    _name = 'credit.limit.rule.wizard'
    _description = 'Remake the sequence of Journal Entries.'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    sale_order_id = fields.Many2one(comodel_name='sale.order')
    account_move_id = fields.Many2one(comodel_name='account.move')

    company_id = fields.Many2one(comodel_name='res.company',
                                 string='Company',
                                 default=lambda self: self.env.user.company_id )
    currency_id = fields.Many2one(string='Currency',
                                  readonly=True,
                                  related='company_id.currency_id')

    credit_limit = fields.Monetary(string='Amount Credit Limit')

    amount_receivable = fields.Monetary()
    amount_current_quotation = fields.Monetary()
    amount_exceeded = fields.Monetary()
    amount_available = fields.Monetary()


    doc_limit = fields.Integer(string='Document Limit')
    doc_available = fields.Integer()

    sale_orders = fields.Char()
    account_moves = fields.Char()

    def action_approve_document(self):
        if self.account_move_id:
            self.account_move_id.allow_credit
            return True

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.account_move_id:
            rules = self.partner_id.credit_limit_rules_ids
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
                self.doc_limit = minimo_doc
            if len(limite) > 0:
                limite.sort()
                limite_credito = limite[0]
                amount_doc = 0.0

                # Sumo el monto de las facturas
                for inv in invoices:
                    amount_doc += inv.amount_residual_signed
                self.account_moves = f"{len(invoices)} Invoices - Amount Residual {round(amount_doc, 2)}"
                self.doc_available = self.doc_limit - len(invoices)
                self.credit_limit = limite_credito
                self.amount_receivable = round(amount_doc, 2)
                self.amount_current_quotation =  round(self.account_move_id.amount_residual_signed, 2)

                self.amount_available = self.credit_limit - self.amount_receivable
                if self.amount_available < 0.0:
                    self.amount_exceeded =  round(self.amount_receivable - self.amount_current_quotation, 2)
            # return True
        if self.sale_order_id:
            pass