from odoo import models, api, fields, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    has_account_move = fields.Boolean(string='Has Account Move', compute='_compute_has_account_move', store=True)

    @api.depends('account_move')
    def _compute_has_account_move(self):
        for order in self:
            order.has_account_move = bool(order.account_move)

    def settle_customer_account(self):
        for order in self:
            if order.state == 'paid':
                return True
        return False

    def action_open_account_statement(self):
        # Logique pour ouvrir l'état de compte du client
        self.ensure_one()
        action = self.env.ref('pos_settle_customer_account.action_account_statement').read()[0]
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_pos_order_id': self.id,
        }
        return action

    def action_report_account_statement(self):
        unpaid_orders = self.env['pos.order'].search([('partner_id', '=', self.id), ('state', '!=', 'paid')])
        return self.env.ref('pos_settle_customer_account.action_report_account_statement').report_action(self, data={
            'orders': unpaid_orders.ids})

    def action_generate_invoice(self):
        # Logique pour générer une facture de régularisation à partir des commandes sélectionnées
        for order in self:
            if not order.invoice_id:
                pass
        pass

    def action_generate_invoice_and_statement(self):
        self.action_generate_invoice()

    def create_due_invoice(self):
        # Group all orders by partner
        orders_by_partner = {}
        invoice_ids = []
        for order in self:
            if not order.account_move:
                if order.partner_id not in orders_by_partner:
                    orders_by_partner[order.partner_id] = order
                else:
                    orders_by_partner[order.partner_id] |= order
        # Create an invoice for each partner
        for partner, orders in orders_by_partner.items():
            # Group orders lines by taxes
            taxes = {}
            for order in orders:
                for line in order.lines:
                    for tax in line.tax_ids:
                        if tax not in taxes:
                            taxes[tax] = line
                        else:
                            taxes[tax] |= line

            # Create invoice lines
            invoice_lines = []
            for tax, lines in taxes.items():
                months = set()
                # Get all months of orders
                for line in lines:
                    months.add(line.order_id.date_order.strftime('%B %Y'))
                # If only one month label is _('Orders of %s') % month else _('Orders of each month')
                if len(months) == 1:
                    label = _('Orders of month: %s') % months.pop()
                else:
                    label = _('Orders of months: %s') % ', '.join(months)

                invoice_lines.append((0, 0, {
                    'product_id': self.env.ref('pos_settle_customer_account.product_settle_customer_account').id,
                    'name': label,
                    'quantity': 1,
                    'price_unit': sum(lines.mapped('price_subtotal_incl')),
                    'tax_ids': [(6, 0, tax.ids)],
                }))

            account_move = self.env['account.move'].create({
                'partner_id': partner.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
                'pos_order_ids': [(6, 0, orders.ids)],
            })
            account_move.action_post()
            for order in orders:
                order.account_move = account_move.id
                order.state = 'invoiced'
            invoice_ids.append(account_move.id)

        return {
            'name': _('Customer Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoice_ids)],
        }
