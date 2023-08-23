# -*- coding: utf-8 -*-
{
    'name': 'PoS Event Sale Ticket Order',
    'version': '15.0.1.0.0',
    'category': 'Custom',
    'summary': 'PoS Event Sale Ticket Order',
    'description': "Organize event tickets order",
    'depends': ['event_ticket_order', 'pos_event_sale'],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    "assets": {
        "point_of_sale.assets": [
            "pos_event_sale_ticket_order/static/src/js/**/*.js",
            "pos_event_sale_ticket_order/static/src/scss/**/*.scss",
        ],
        "web.assets_qweb": [
            "pos_event_sale_ticket_order/static/src/xml/**/*.xml",
        ],
        "web.assets_tests": [
            "pos_event_sale_ticket_order/static/tests/tours/**/*",
        ],
    },
}
