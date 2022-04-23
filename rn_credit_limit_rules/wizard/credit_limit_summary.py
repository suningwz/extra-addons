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

    account_moves = fields.Char()

    def action_approve_document(self):
        if self.account_move_id:
            self.account_move_id.allow_credit = True
            return True
        if self.sale_order_id:
            self.sale_order_id.allow_credit = True
            return True

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        invoices = self.env['account.move'].sudo().search([
                # Facturas y Notas de Crédito
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                # Donde el monto adeudado sea distinto a 0
                ('amount_residual_signed', '<>', 0.0),
                # Documento esté publicado
                ('state', '=', 'posted')])
        if self.account_move_id:
            if self.partner_id.credit_limit_rules_id.type == 'amount':
                limite_credito = self.partner_id.credit_limit_rules_id.credit_limit
                amount_doc = 0.0
                # Convertirmos el monto a la moneda de la compañía
                if self.account_move_id.currency_id.id != self.company_id.currency_id.id:
                    amount_doc = 1 / self.account_move_id.currency_rate * self.account_move_id.amount_residual_signed
                else:
                    amount_doc = self.account_move_id.amount_residual_signed
                current_document = amount_doc

                # Sumo el monto de las facturas
                for inv in invoices:
                    amount_doc += inv.amount_residual_signed
                self.account_moves = f"{len(invoices)} Invoices - Amount Receivable {round(amount_doc - current_document, 2)}"
                available = self.doc_limit - len(invoices)
                self.doc_available = available if available > 0.0 else 0.0
                self.credit_limit = limite_credito
                self.amount_receivable = round(amount_doc - current_document, 2)
                self.amount_current_quotation =  round(current_document, 2)

                self.amount_available = self.credit_limit - self.amount_receivable
                self.amount_exceeded =  round(self.amount_current_quotation - self.amount_available, 2)

            if self.partner_id.credit_limit_rules_id.type == 'documents':
                minimo_doc = self.partner_id.credit_limit_rules_id.doc_limit
                self.doc_limit = minimo_doc
                amount_doc = 0.0
                # Convertirmos el monto a la moneda de la compañía
                if self.account_move_id.currency_id.id != self.company_id.currency_id.id:
                    amount_doc = 1 / self.account_move_id.currency_rate * self.account_move_id.amount_residual_signed
                else:
                    amount_doc = self.account_move_id.amount_residual_signed
                current_document = amount_doc

                # Sumo el monto de las facturas
                for inv in invoices:
                    amount_doc += inv.amount_residual_signed
                self.account_moves = f"{len(invoices)} Invoices - Amount Receivable {round(amount_doc - current_document, 2)}"
                self.amount_receivable = round(amount_doc - current_document, 2)
                self.amount_current_quotation =  round(current_document, 2)
                self.doc_available = minimo_doc - len(invoices)

        if self.sale_order_id:
            if self.partner_id.credit_limit_rules_id.type == 'amount':
                limite_credito = self.partner_id.credit_limit_rules_id.credit_limit
                amount_doc = 0.0
                # Convertirmos el monto a la moneda de la compañía
                if self.sale_order_id.currency_id.id != self.company_id.currency_id.id:
                    amount_doc = 1 / self.sale_order_id.currency_rate * self.sale_order_id.amount_total
                else:
                    amount_doc = self.sale_order_id.amount_total
                current_document = amount_doc

                # Sumo el monto de las facturas
                for inv in invoices:
                    amount_doc += inv.amount_residual_signed
                self.account_moves = f"{len(invoices)} Invoices - Amount Receivable {round(amount_doc - current_document, 2)}"
                available = self.doc_limit - len(invoices)
                self.doc_available = available if available > 0.0 else 0.0
                self.credit_limit = limite_credito
                self.amount_receivable = round(amount_doc - current_document, 2)
                self.amount_current_quotation =  round(current_document, 2)

                self.amount_available = self.credit_limit - self.amount_receivable
                self.amount_exceeded =  round(self.amount_current_quotation - self.amount_available, 2)

            if self.partner_id.credit_limit_rules_id.type == 'documents':
                minimo_doc = self.partner_id.credit_limit_rules_id.doc_limit
                self.doc_limit = minimo_doc
                amount_doc = 0.0
                # Convertirmos el monto a la moneda de la compañía
                if self.sale_order_id.currency_id.id != self.company_id.currency_id.id:
                    amount_doc = 1 / self.sale_order_id.currency_rate * self.sale_order_id.amount_total
                else:
                    amount_doc = self.sale_order_id.amount_total
                current_document = amount_doc

                # Sumo el monto de las facturas
                for inv in invoices:
                    amount_doc += inv.amount_residual_signed
                self.amount_receivable = round(amount_doc - current_document, 2)
                self.account_moves = f"{len(invoices)} Invoices - Amount Receivable {round(amount_doc - current_document, 2)}"
                self.amount_current_quotation =  round(current_document, 2)
                self.doc_available = minimo_doc - len(invoices)
