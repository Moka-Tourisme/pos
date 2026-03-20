# Copyright 2025 - Moka Tourisme
# License LGPL-3 - See LICENSE file for full copyright and licensing details.

from odoo import models

# Couleur d'en-tête : jaune pâle selon spécification
HEADER_BG_COLOR = '#FFFFCC'
HEADER_FONT_BOLD = True
CURRENCY_FORMAT = '#,##0.00 €'
INTEGER_FORMAT = '#,##0'


class ReportPosPaymentVatXlsx(models.AbstractModel):
    _name = 'report.pos.payment.vat.wizard.xlsx'
    _description = 'Rapport XLSX - Ventes POS par Mode de Paiement et TVA'
    _inherit = 'report.report_xlsx.abstract'

    def _get_report_data(self, wizard):
        """Récupère et retourne les lignes filtrées du rapport."""
        domain = [
            ('date', '>=', wizard.date_from),
            ('date', '<=', wizard.date_to),
        ]
        if wizard.pos_config_ids:
            domain.append(('pos_config_id', 'in', wizard.pos_config_ids.ids))

        return self.env['pos.payment.vat.report'].search(
            domain,
            order='date asc, payment_method_id asc, tax_rate asc',
        )

    def _get_header_format(self, workbook):
        """Format en-tête : gras, fond jaune pâle, bordure."""
        fmt = workbook.add_format({
            'bold': True,
            'bg_color': HEADER_BG_COLOR,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        return fmt

    def _get_total_format(self, workbook):
        """Format ligne totaux : gras, fond gris clair."""
        fmt = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1,
            'num_format': CURRENCY_FORMAT,
        })
        return fmt

    def _get_total_label_format(self, workbook):
        """Format libellé totaux : gras, fond gris clair."""
        fmt = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1,
        })
        return fmt

    def _get_money_format(self, workbook):
        """Format montant monétaire standard."""
        return workbook.add_format({
            'num_format': CURRENCY_FORMAT,
            'border': 1,
        })

    def _get_cell_format(self, workbook):
        """Format cellule standard avec bordure."""
        return workbook.add_format({'border': 1})

    def _get_int_format(self, workbook):
        """Format entier avec bordure."""
        return workbook.add_format({
            'num_format': INTEGER_FORMAT,
            'border': 1,
        })

    def _write_summary_sheet(self, workbook, lines):
        """
        Feuille 1 : tableau croisé
          - Lignes  : taux de TVA
          - Colonnes : modes de paiement
          - Mesures  : CA TTC, TVA collectée, CA HT par cellule
        """
        sheet = workbook.add_worksheet('Récapitulatif')
        header_fmt = self._get_header_format(workbook)
        money_fmt = self._get_money_format(workbook)
        total_fmt = self._get_total_format(workbook)
        total_lbl_fmt = self._get_total_label_format(workbook)
        cell_fmt = self._get_cell_format(workbook)

        # Collecte des valeurs distinctes triées
        tax_rates = sorted(set(l.tax_rate for l in lines))
        payment_methods = sorted(
            set((l.payment_method_id.id, l.payment_method_id.name) for l in lines),
            key=lambda x: x[1],
        )

        # --- Construction de l'index des données ---
        # data[tax_rate][pm_id] = {'ttc': 0, 'tax': 0, 'ht': 0}
        data = {}
        for rate in tax_rates:
            data[rate] = {}
            for pm_id, _pm_name in payment_methods:
                data[rate][pm_id] = {'ttc': 0.0, 'tax': 0.0, 'ht': 0.0}

        for line in lines:
            rate = line.tax_rate
            pm_id = line.payment_method_id.id
            data[rate][pm_id]['ttc'] += line.amount_total_ttc
            data[rate][pm_id]['tax'] += line.amount_tax
            data[rate][pm_id]['ht'] += line.amount_total_ht

        # --- En-têtes colonnes ---
        # Ligne 0 : titre module de paiement (fusion sur 3 colonnes par mode)
        # Ligne 1 : sous-titres CA TTC / TVA / CA HT
        col_start = 1  # Colonne 0 réservée pour le taux TVA

        sheet.write(0, 0, 'Taux TVA', header_fmt)
        sheet.write(1, 0, '', header_fmt)

        pm_col_map = {}
        for idx, (pm_id, pm_name) in enumerate(payment_methods):
            col = col_start + idx * 3
            pm_col_map[pm_id] = col
            sheet.merge_range(0, col, 0, col + 2, pm_name, header_fmt)
            sheet.write(1, col, 'CA TTC', header_fmt)
            sheet.write(1, col + 1, 'TVA', header_fmt)
            sheet.write(1, col + 2, 'CA HT', header_fmt)

        # Colonnes totaux
        total_col = col_start + len(payment_methods) * 3
        sheet.merge_range(0, total_col, 0, total_col + 2, 'TOTAL', header_fmt)
        sheet.write(1, total_col, 'CA TTC', header_fmt)
        sheet.write(1, total_col + 1, 'TVA', header_fmt)
        sheet.write(1, total_col + 2, 'CA HT', header_fmt)

        # --- Lignes de données ---
        row = 2
        grand_total = {'ttc': 0.0, 'tax': 0.0, 'ht': 0.0}
        pm_totals = {pm_id: {'ttc': 0.0, 'tax': 0.0, 'ht': 0.0} for pm_id, _ in payment_methods}

        for rate in tax_rates:
            rate_label = '{}%'.format(rate).replace('.0%', '%')
            sheet.write(row, 0, rate_label, cell_fmt)
            row_ttc = row_tax = row_ht = 0.0

            for pm_id, _pm_name in payment_methods:
                col = pm_col_map[pm_id]
                vals = data[rate][pm_id]
                sheet.write(row, col, vals['ttc'], money_fmt)
                sheet.write(row, col + 1, vals['tax'], money_fmt)
                sheet.write(row, col + 2, vals['ht'], money_fmt)
                row_ttc += vals['ttc']
                row_tax += vals['tax']
                row_ht += vals['ht']
                pm_totals[pm_id]['ttc'] += vals['ttc']
                pm_totals[pm_id]['tax'] += vals['tax']
                pm_totals[pm_id]['ht'] += vals['ht']

            # Total ligne
            sheet.write(row, total_col, row_ttc, money_fmt)
            sheet.write(row, total_col + 1, row_tax, money_fmt)
            sheet.write(row, total_col + 2, row_ht, money_fmt)
            grand_total['ttc'] += row_ttc
            grand_total['tax'] += row_tax
            grand_total['ht'] += row_ht
            row += 1

        # --- Ligne de totaux ---
        sheet.write(row, 0, 'TOTAL', total_lbl_fmt)
        for pm_id, _pm_name in payment_methods:
            col = pm_col_map[pm_id]
            sheet.write(row, col, pm_totals[pm_id]['ttc'], total_fmt)
            sheet.write(row, col + 1, pm_totals[pm_id]['tax'], total_fmt)
            sheet.write(row, col + 2, pm_totals[pm_id]['ht'], total_fmt)
        sheet.write(row, total_col, grand_total['ttc'], total_fmt)
        sheet.write(row, total_col + 1, grand_total['tax'], total_fmt)
        sheet.write(row, total_col + 2, grand_total['ht'], total_fmt)

        # Ajustement largeur colonnes
        sheet.set_column(0, 0, 14)
        for idx in range(len(payment_methods) + 1):
            base_col = col_start + idx * 3
            sheet.set_column(base_col, base_col + 2, 14)

    def _write_detail_sheet(self, workbook, lines):
        """
        Feuille 2 : détail ligne à ligne avec totaux en bas.
        Colonnes : Date | POS | Mode de paiement | Taxe | Taux TVA | Nb commandes
                   | CA TTC | TVA collectée | CA HT
        """
        sheet = workbook.add_worksheet('Détail')
        header_fmt = self._get_header_format(workbook)
        money_fmt = self._get_money_format(workbook)
        total_fmt = self._get_total_format(workbook)
        total_lbl_fmt = self._get_total_label_format(workbook)
        cell_fmt = self._get_cell_format(workbook)
        int_fmt = self._get_int_format(workbook)

        headers = [
            'Date',
            'Point de Vente',
            'Mode de Paiement',
            'Taxe',
            'Taux TVA (%)',
            'Nb Commandes',
            'CA TTC',
            'TVA collectée',
            'CA HT',
        ]
        col_widths = [12, 20, 22, 20, 14, 16, 14, 14, 14]

        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_fmt)
            sheet.set_column(col, col, col_widths[col])

        totals = {'nb_orders': 0, 'ttc': 0.0, 'tax': 0.0, 'ht': 0.0}
        row = 1

        for line in lines:
            sheet.write(row, 0, str(line.date) if line.date else '', cell_fmt)
            sheet.write(row, 1, line.pos_config_id.name or '', cell_fmt)
            sheet.write(row, 2, line.payment_method_id.name or '', cell_fmt)
            sheet.write(row, 3, line.tax_id.name or '', cell_fmt)
            sheet.write(row, 4, line.tax_rate, cell_fmt)
            sheet.write(row, 5, line.nb_orders, int_fmt)
            sheet.write(row, 6, line.amount_total_ttc, money_fmt)
            sheet.write(row, 7, line.amount_tax, money_fmt)
            sheet.write(row, 8, line.amount_total_ht, money_fmt)

            totals['nb_orders'] += line.nb_orders
            totals['ttc'] += line.amount_total_ttc
            totals['tax'] += line.amount_tax
            totals['ht'] += line.amount_total_ht
            row += 1

        # Ligne de totaux
        sheet.write(row, 0, 'TOTAL', total_lbl_fmt)
        for col in range(1, 5):
            sheet.write(row, col, '', total_lbl_fmt)
        sheet.write(row, 5, totals['nb_orders'], total_fmt)
        sheet.write(row, 6, totals['ttc'], total_fmt)
        sheet.write(row, 7, totals['tax'], total_fmt)
        sheet.write(row, 8, totals['ht'], total_fmt)

    def generate_xlsx_report(self, workbook, data, wizards):
        """Point d'entrée appelé par report_xlsx pour générer le fichier Excel."""
        for wizard in wizards:
            lines = self._get_report_data(wizard)
            self._write_summary_sheet(workbook, lines)
            self._write_detail_sheet(workbook, lines)
