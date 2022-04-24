from odoo import models, _

from datetime import date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cancel_so_expired(self):
        now = date.today()
        sale_orders = self.env['sale.order'].sudo().search([('state', 'in', ('draft', 'sent', 'sale')),
                                                            ('validity_date', '<', now)])

        for order in sale_orders:

            order.state = 'cancel'
            body = _("The sale order was canceled because the expiration date passed")
            order.message_post(body=body, message_type="notification")
