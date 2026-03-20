# Copyright 2025 - Moka Tourisme
# License LGPL-3 - See LICENSE file for full copyright and licensing details.

{
    'name': 'POS - Rapport Ventes par Mode de Paiement et TVA',
    'version': '16.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Rapport croisant modes de paiement et taux de TVA collectée',
    'author': 'Moka Tourisme',
    'website': 'https://www.mokatourisme.fr',
    'depends': ['point_of_sale', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_vat_report_views.xml',
        'wizard/pos_payment_vat_wizard_views.xml',
        'report/pos_payment_vat_report.xml',
        'report/pos_payment_vat_pdf.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pos_sale_payment_vat_report/static/src/js/pivot_patch.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
