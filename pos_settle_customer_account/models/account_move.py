from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_order_ids = fields.One2many(
        'pos.order',
        'account_move',
        string='POS Orders',
        help='POS Orders linked to this invoice'
    )

    def action_send_customer_account_invoice(self):
        """Send the customer account invoice with the regularisation report attached."""
        self.ensure_one()

        if not self.pos_order_ids:
            raise UserError(_("This invoice is not linked to any POS orders."))

        # Create or get existing attachment
        attachment = self._prepare_regularisation_attachment()

        # Get email template
        template = self.env.ref('pos_settle_customer_account.email_template_edi_invoice', raise_if_not_found=False)

        # Prepare email composer context
        composer_ctx = dict(
            self.env.context,
            default_model='account.move',
            default_res_ids=self.ids,
            default_partner_ids=[(6, 0, [self.partner_id.id])] if self.partner_id else [],
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            default_email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
        )

        if template:
            composer_ctx['default_template_id'] = template.id

        if attachment:
            composer_ctx['default_attachment_ids'] = [(6, 0, [attachment.id])]

        # Open the email composer
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send Customer Account Invoice'),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': composer_ctx,
        }

    def _prepare_regularisation_attachment(self):
        """Generate and return the regularisation PDF as an attachment."""
        self.ensure_one()

        # Check if attachment already exists
        existing_attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('name', 'like', 'Regularisation_%')
        ], limit=1)

        if existing_attachment:
            return existing_attachment

        # Generate PDF using the standard Odoo report method
        try:
            report_sudo = self.env['ir.actions.report'].sudo()
            pdf_content = report_sudo._render_qweb_pdf(
                'pos_settle_customer_account.report_pos_order_regularisation',
                self.ids
            )[0]

            # Create the attachment
            attachment_name = 'Regularisation_%s.pdf' % self.name.replace('/', '_')
            attachment = self.env['ir.attachment'].create({
                'name': attachment_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'account.move',
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })

            return attachment

        except Exception as e:
            _logger.error("Error generating regularisation PDF for invoice %s: %s", self.name, str(e))
            # Return None if PDF generation fails - email can still be sent without it
            return None

    def _message_auto_subscribe_notify(self, partner_ids, template):
        """Override to attach regularisation report when sending invoice notification."""
        # Check if this is a customer account invoice (has pos_order_ids)
        if self.pos_order_ids and template == self.env.ref('pos_settle_customer_account.email_template_edi_invoice', raise_if_not_found=False):
            # Generate and attach the regularisation report
            report = self.env.ref('pos_settle_customer_account.action_generate_regularisation', raise_if_not_found=False)
            if report:
                try:
                    pdf_content, content_type = report._render_qweb_pdf([self.id])
                    attachment = self.env['ir.attachment'].create({
                        'name': f"Invoice_{self.name.replace('/', '_')}.pdf",
                        'type': 'binary',
                        'datas': base64.b64encode(pdf_content),
                        'res_model': 'account.move',
                        'res_id': self.id,
                        'mimetype': 'application/pdf',
                    })
                    # The attachment will be automatically included in the email
                except Exception:
                    pass  # If report generation fails, continue without it

        return super()._message_auto_subscribe_notify(partner_ids, template)
