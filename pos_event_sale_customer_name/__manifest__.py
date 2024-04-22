{
    "name": "POS Event Sale Customer Name",
    "version": "15.0.0.0.1",
    "author": "Moka",
    "category": "Point Of Sale",
    "website": "https://github.com/OCA/event",
    "license": "AGPL-3",
    "depends": ["pos_event_sale"],
    "assets": {
        "web.assets_qweb":[
            "pos_event_sale_customer_name/static/src/xml/**/*.xml",
        ]
    },
    'installable': True,
    'auto_install': False,
}
