# Copyright 2024 Moka - Horvat Damien
# Copyright 2024 Moka - Duciell Romain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'POS Settle Customer Account',
    'summary': 'Invoice customer accounts and generate sales statements and collective invoices',
    'version': '16.0.0.0.1',
    'category': 'Point of Sale/Accounting',
    "author": "Moka",
    "website": "https://www.mokatourisme.fr",
    'depends': ['point_of_sale', 'account', 'uom', 'product', 'website_sale'],
    'data': [
        'data/product_data.xml',
        'report/report_pos_client_statement.xml',
        'views/report_invoice.xml',
        'views/pos_order_view.xml',
        'views/pos_config_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
