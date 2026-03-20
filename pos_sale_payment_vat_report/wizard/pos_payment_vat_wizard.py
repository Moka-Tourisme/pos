# Copyright 2025 - Moka Tourisme
# License LGPL-3 - See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models


class PosPaymentVatWizard(models.TransientModel):
    _name = 'pos.payment.vat.wizard'
    _description = 'Assistant Export XLSX - Ventes POS par Mode de Paiement et TVA'

    date_from = fields.Date(
        string='Date de début',
        required=True,
        default=lambda self: date.today().replace(day=1),
    )
    date_to = fields.Date(
        string='Date de fin',
        required=True,
        default=fields.Date.today,
    )
    pos_config_ids = fields.Many2many(
        comodel_name='pos.config',
        string='Points de Vente',
        help='Laisser vide pour inclure tous les points de vente.',
    )

    def action_export_xlsx(self):
        """Déclenche la génération du rapport XLSX."""
        self.ensure_one()
        return self.env.ref(
            'pos_sale_payment_vat_report.action_pos_payment_vat_xlsx'
        ).report_action(self)

    def action_print_pdf(self):
        """Déclenche la génération du rapport PDF."""
        self.ensure_one()
        return self.env.ref(
            'pos_sale_payment_vat_report.action_pos_payment_vat_pdf'
        ).report_action(self)

    def _get_pdf_data(self):
        """Prépare les données structurées pour le template QWeb PDF.
        Retourne une section par mode de paiement, chacune ventilée par taux TVA.
        """
        self.ensure_one()
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.pos_config_ids:
            domain.append(('pos_config_id', 'in', self.pos_config_ids.ids))

        lines = self.env['pos.payment.vat.report'].search(
            domain, order='payment_method_id asc, tax_rate asc'
        )

        # Agrégation par (mode de paiement, taux TVA) sur toute la période
        # sections_data[pm_id] = {'pm_name': ..., 'rows': {tax_rate: {...}}}
        sections_data = {}
        grand_total = {'ttc': 0.0, 'tax': 0.0, 'ht': 0.0, 'nb': 0}

        for line in lines:
            pm_id = line.payment_method_id.id
            pm_name = line.payment_method_id.name
            tax_rate = line.tax_rate

            if pm_id not in sections_data:
                sections_data[pm_id] = {'pm_name': pm_name, 'rows': {}}

            if tax_rate not in sections_data[pm_id]['rows']:
                sections_data[pm_id]['rows'][tax_rate] = {
                    'tax_label': '%g%%' % tax_rate,
                    'ttc': 0.0, 'tax': 0.0, 'ht': 0.0, 'nb': 0,
                }

            row = sections_data[pm_id]['rows'][tax_rate]
            row['ttc'] += line.amount_total_ttc
            row['tax'] += line.amount_tax
            row['ht'] += line.amount_total_ht
            row['nb'] += line.nb_orders

            grand_total['ttc'] += line.amount_total_ttc
            grand_total['tax'] += line.amount_tax
            grand_total['ht'] += line.amount_total_ht
            grand_total['nb'] += line.nb_orders

        # Construction des sections triées par nom de mode de paiement
        sections = []
        for pm_id, sec in sorted(sections_data.items(), key=lambda x: x[1]['pm_name']):
            rows = sorted(sec['rows'].values(), key=lambda r: r['tax_label'])
            sections.append({
                'pm_name': sec['pm_name'],
                'rows': rows,
                'total_ttc': sum(r['ttc'] for r in rows),
                'total_tax': sum(r['tax'] for r in rows),
                'total_ht': sum(r['ht'] for r in rows),
                'total_nb': sum(r['nb'] for r in rows),
            })

        return {
            'sections': sections,
            'grand_total': grand_total,
        }
