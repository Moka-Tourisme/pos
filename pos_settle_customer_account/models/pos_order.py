from odoo import models, api, fields, _
import pytz


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
            print(partner, orders)
            orders.action_pos_order_invoice_multi(partner)

        return {
            'name': _('Customer Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoice_ids)],
        }

    def action_pos_order_invoice_multi(self, partner):
        for order in self:
            order.write({'to_invoice': True})
            if order.company_id.anglo_saxon_accounting and order.session_id.update_stock_at_closing and order.session_id.state != 'closed':
                order._create_order_picking()
        return self._generate_pos_order_invoice_multi(partner)

    def _generate_pos_order_invoice_multi(self, partner):
        moves = self.env['account.move']
        move_vals = self._prepare_invoice_vals_settle(orders=self, partner=partner)
        print("move_vals: ", move_vals)
        new_move = self.env['account.move'].create(move_vals)
        new_move.sudo().with_context(skip_invoice_sync=True)._post()
        for order in self:
            print("=== Order: ===", order)
            # Force company for all SUPERUSER_ID action
            print("=== Order avant if: ===", order)
            if order.account_move:
                print("=== Order.account_move: ===", order.account_move)
                moves += order.account_move
                continue
            print("=== Order après if: ===", order)
            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            order.write({'account_move': new_move.id, 'state': 'invoiced'})
            moves += new_move
            payment_moves = order._apply_invoice_payments(order.session_id.state == 'closed')
            print("=== ICI avant le if ===")
            if order.session_id.state == 'closed':  # If the session isn't closed this isn't needed.
                # If a client requires the invoice later, we need to revers the amount from the closing entry, by making a new entry for that.
                print("=== ICI dans le if ===")
                order._create_misc_reversal_move(payment_moves)
                print("=== ICI après le if ===")

        if not moves:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': moves and moves.ids[0] or False,
        }

    def prepare_invoice_lines_settle(self, orders):
        invoice_lines = []
        for order in orders:
            invoice_lines.append((0, None, {
                'name': _('Commande du %s', order.date_order.strftime('%d/%m/%Y')),
                'display_type': 'line_section',
            }))
            for line in order.lines:
                invoice_lines.append((0, None, order._prepare_invoice_line(line)))
                if line.order_id.pricelist_id.discount_policy == 'without_discount' and float_compare(line.price_unit,
                                                                                                      line.product_id.lst_price,
                                                                                                      precision_rounding=self.currency_id.rounding) < 0:
                    invoice_lines.append((0, None, {
                        'name': _('Price discount from %s -> %s',
                                  float_repr(line.product_id.lst_price, order.currency_id.decimal_places),
                                  float_repr(line.price_unit, order.currency_id.decimal_places)),
                        'display_type': 'line_note',
                    }))
                if line.customer_note:
                    invoice_lines.append((0, None, {
                        'name': line.customer_note,
                        'display_type': 'line_note',
                    }))
        return invoice_lines

    def _prepare_invoice_vals_settle(self, orders, partner):
        # timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        # invoice_date = fields.Datetime.now() if self.session_id.state == 'closed' else self.date_order
        vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': self.prepare_invoice_lines_settle(orders),
            'state': 'draft',
            # 'pos_order_ids': [(6, 0, orders.ids)],
        }
        # if self.refunded_order_ids.account_move:
        #     vals['ref'] = _('Reversal of: %s', self.refunded_order_ids.account_move.name)
        #     vals['reversed_entry_id'] = self.refunded_order_ids.account_move.id
        # if self.note:
        #     vals.update({'narration': self.note})
        return vals
