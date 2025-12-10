from odoo import models, api, fields, _
from collections import defaultdict
import pytz
import logging
from odoo.tools import float_compare, float_round, float_repr, float_is_zero

_logger = logging.getLogger(__name__)


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
            data = orders.action_pos_order_invoice_multi(partner)
        #     Filter out the invoices that were just created and unique
            invoice_ids += [inv.id for inv in data if inv not in invoice_ids]

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

    def _create_misc_reversal_move(self, payment_moves, **kwargs):
        """ Create a misc move to reverse this POS order and "remove" it from the POS closing entry.
        This is done by taking data from the order and using it to somewhat replicate the resulting entry in order to
        reverse partially the movements done in the POS closing entry.
        """
        aml_values_list_per_nature = self._prepare_aml_values_list_per_nature()
        move_lines = []
        for aml_values_list in aml_values_list_per_nature.values():
            for aml_values in aml_values_list:
                aml_values['balance'] = -aml_values['balance']
                aml_values['amount_currency'] = -aml_values['amount_currency']
                move_lines.append(aml_values)

        # Make a move with all the lines.
        reversal_entry = self.env['account.move'].with_context(
            default_journal_id=self.config_id.journal_id.id,
            skip_invoice_sync=True,
            skip_invoice_line_sync=True,
        ).create({
            'journal_id': self.config_id.journal_id.id,
            'date': fields.Date.context_today(self),
            'ref': _('Reversal of POS closing entry %s for order %s from session %s', self.session_move_id.name,
                     self.name, self.session_id.name),
            'invoice_line_ids': [(0, 0, aml_value) for aml_value in move_lines],
        })
        reversal_entry.action_post()

        pos_account_receivable = self.company_id.account_default_pos_receivable_account_id
        account_receivable = self.payment_ids.payment_method_id.receivable_account_id
        reversal_entry_receivable = reversal_entry.line_ids.filtered(
            lambda l: l.account_id in (pos_account_receivable + account_receivable))
        payment_receivable = payment_moves.line_ids.filtered(
            lambda l: l.account_id in (pos_account_receivable + account_receivable))

        lines_to_reconcile = defaultdict(lambda: self.env['account.move.line'])
        for line in (reversal_entry_receivable | payment_receivable):
            lines_to_reconcile[line.account_id] |= line

        if kwargs.get("to_reconcile"):
            self._reconcile_customer_account_lines(reversal_entry)

        for line in lines_to_reconcile.values():
            line.filtered(lambda l: not l.reconciled).reconcile()

        return reversal_entry

    def _reconcile_customer_account_lines(self, reversal_entry):
        """Reconcile customer account lines between reversal entry and session move.

        This method finds matching lines in the session move and reversal entry
        for the customer receivable account and reconciles them.

        Important: Uses commercial_partner_id for matching because Odoo uses the
        commercial partner (parent company) for accounting entries, not the contact.
        """
        currency = self.currency_id
        # Use commercial_partner_id (parent company) for accounting, not the contact directly
        commercial_partner = self.partner_id.commercial_partner_id
        # Get receivable account from the accounting partner (same as Odoo standard)
        accounting_partner = self.env["res.partner"]._find_accounting_partner(self.partner_id)
        receivable_account = accounting_partner.with_company(self.company_id).property_account_receivable_id

        if not receivable_account:
            _logger.warning(
                "POS Order %s: Partner %s (commercial: %s) has no receivable account configured, skipping reconciliation",
                self.name, self.partner_id.name, commercial_partner.name
            )
            return

        _logger.info(
            "POS Order %s: Looking for lines to reconcile - Partner: %s, Commercial Partner: %s, Account: %s",
            self.name, self.partner_id.name, commercial_partner.name, receivable_account.code
        )

        # Find reversal lines for this partner's receivable account
        # Check both the contact and the commercial partner
        reversal_lines = reversal_entry.line_ids.filtered(
            lambda l: l.account_id == receivable_account
            and l.partner_id in (self.partner_id, commercial_partner)
            and not l.reconciled
        )

        if not reversal_lines:
            _logger.warning(
                "POS Order %s: No reversal lines found for partner %s/%s on account %s. "
                "Reversal entry lines: %s",
                self.name, self.partner_id.name, commercial_partner.name, receivable_account.code,
                [(l.partner_id.name, l.account_id.code, l.balance) for l in reversal_entry.line_ids]
            )
            return

        # Find matching session move lines
        # Check both the contact and the commercial partner
        session_lines = self.session_move_id.line_ids.filtered(
            lambda l: l.account_id == receivable_account
            and l.partner_id in (self.partner_id, commercial_partner)
            and not l.reconciled
        )

        if not session_lines:
            _logger.warning(
                "POS Order %s: No session move lines found for partner %s/%s on account %s. "
                "Session move lines: %s",
                self.name, self.partner_id.name, commercial_partner.name, receivable_account.code,
                [(l.partner_id.name, l.account_id.code, l.balance, l.reconciled)
                 for l in self.session_move_id.line_ids.filtered(lambda l: l.account_id == receivable_account)]
            )
            return

        _logger.info(
            "POS Order %s: Found %d reversal lines and %d session lines to reconcile",
            self.name, len(reversal_lines), len(session_lines)
        )

        # Try to find matching lines by amount (with tolerance for rounding)
        for reversal_line in reversal_lines:
            reversal_balance = reversal_line.balance
            matching_session_line = None

            for session_line in session_lines:
                # Check if balances are opposite (should sum to zero)
                if float_is_zero(session_line.balance + reversal_balance, precision_rounding=currency.rounding):
                    matching_session_line = session_line
                    break

            if matching_session_line:
                lines_to_reconcile = reversal_line | matching_session_line
                try:
                    lines_to_reconcile.reconcile()
                    _logger.info(
                        "POS Order %s: Successfully reconciled lines for partner %s (amount: %s)",
                        self.name, commercial_partner.name, abs(reversal_balance)
                    )
                except Exception as e:
                    _logger.error(
                        "POS Order %s: Failed to reconcile lines for partner %s: %s",
                        self.name, commercial_partner.name, str(e)
                    )
            else:
                # No exact match found, try partial reconciliation with available lines
                _logger.warning(
                    "POS Order %s: No exact match found for reversal amount %s. "
                    "Session lines balances: %s. Attempting partial reconciliation.",
                    self.name, reversal_balance,
                    [l.balance for l in session_lines]
                )
                # Reconcile all available lines - Odoo will handle partial reconciliation
                all_lines = reversal_line | session_lines
                try:
                    all_lines.filtered(lambda l: not l.reconciled).reconcile()
                except Exception as e:
                    _logger.error(
                        "POS Order %s: Partial reconciliation failed for partner %s: %s",
                        self.name, commercial_partner.name, str(e)
                    )

    def _generate_pos_order_invoice_multi(self, partner):
        moves = self.env['account.move']
        move_vals = self._prepare_invoice_vals_settle(orders=self, partner=partner)
        new_move = self.env['account.move'].create(move_vals)
        new_move.sudo().with_context(skip_invoice_sync=True)._post()

        reconciliation_details = []
        for order in self:
            # Force company for all SUPERUSER_ID action
            if order.account_move:
                moves += order.account_move
                continue
            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            order.write({'account_move': new_move.id, 'state': 'invoiced'})
            moves += new_move
            payment_moves = order._apply_invoice_payments(order.session_id.state == 'closed')
            if order.session_id.state == 'closed':  # If the session isn't closed this isn't needed.
                # If a client requires the invoice later, we need to reverse the amount from the closing entry
                reversal_move = order._create_misc_reversal_move(payment_moves, to_reconcile=True)
                if reversal_move:
                    reconciliation_details.append({
                        'order': order,
                        'reversal_move': reversal_move,
                        'session_move': order.session_move_id,
                    })

        # Post message in invoice chatter with reconciliation details
        if reconciliation_details:
            self._post_reconciliation_message(new_move, reconciliation_details)

        if not moves:
            return {}
        return moves

    def _post_reconciliation_message(self, invoice, reconciliation_details):
        """Post a message in the invoice chatter with reconciliation details."""
        message_lines = [_("<strong>Détail de la réconciliation:</strong><br/>")]

        for detail in reconciliation_details:
            order = detail['order']
            reversal_move = detail['reversal_move']
            session_move = detail['session_move']

            message_lines.append(_(
                "<li><strong>%(order_name)s</strong> (%(amount)s %(currency)s)<br/>"
                "&nbsp;&nbsp;&bull; Extourne: <a href=\"#\" data-oe-model=\"account.move\" data-oe-id=\"%(reversal_id)s\">%(reversal_name)s</a><br/>"
                "&nbsp;&nbsp;&bull; Commande d'origine: <a href=\"#\" data-oe-model=\"account.move\" data-oe-id=\"%(session_id)s\">%(session_name)s</a></li>",
                order_name=order.name,
                amount=order.amount_total,
                currency=order.currency_id.symbol,
                reversal_id=reversal_move.id,
                reversal_name=reversal_move.name,
                session_id=session_move.id,
                session_name=session_move.name,
            ))

        message_body = "<ul>" + "".join(message_lines) + "</ul>"
        invoice.message_post(body=message_body, message_type='comment')

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
