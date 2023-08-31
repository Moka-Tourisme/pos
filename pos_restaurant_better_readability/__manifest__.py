{
    'name': 'Restaurant Ticket Better Readability',
    'version': '15.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Restaurant extensions for the Point of Sale ',
    'depends': ['pos_restaurant'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'point_of_sale.assets': [
            'pos_restaurant_better_readability/static/src/js/models.js',
            'pos_restaurant_better_readability/static/src/css/restaurant.css',
        ],
        'web.assets_qweb': [
            'pos_restaurant_better_readability/static/src/xml/**/*',
        ],
    },
    'license': 'AGPL-3',
}
