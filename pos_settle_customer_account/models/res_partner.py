from odoo import api, fields, models, tools, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    amount_residual = fields.Float(
        string='Residual Amount',
        compute='_compute_amount_residual',
        help="Total residual amount of the customer."
    )

    def action_view_pos_order_dues(self):
        action = self.env['ir.actions.act_window']._for_xml_id('point_of_sale.action_pos_pos_form')
        if self.is_company:
            action['domain'] = [('partner_id.commercial_partner_id', '=', self.id), ('state', '!=', 'paid')]
        else:
            action['domain'] = [('partner_id', '=', self.id), ('state', '!=', 'paid')]
        action['domain'].append(('payment_ids.payment_method_id.split_transactions', '=', True))
        action['domain'].append(('payment_ids.payment_method_id.journal_id', '=', False))
        action['domain'].append(('state', 'in', ['done', 'invoiced']))
        action['domain'].append(('amount_total', '>', 0))
        return action

    @api.depends("pos_order_ids")
    def _compute_amount_residual(self):
        for partner in self:
            customer_account_orders = partner.pos_order_ids.filtered(
                lambda order: order.payment_ids.filtered(lambda payment: payment.payment_method_id.split_transactions))
            customer_account_orders = customer_account_orders.filtered(
                lambda order: order.state == 'done' and order.amount_total > 0)
            partner.amount_residual = sum(customer_account_orders.mapped('amount_total'))
