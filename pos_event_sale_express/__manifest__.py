# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Point of Sale Events Express",
    "summary": "Sell events from Point of Sale",
    "author": "DUCIEL Romain",
    "website": "https://github.com/OCA/pos",
    "category": "Marketing",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["pos_event_sale"],
    "data": [
        "views/pos_config.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_event_sale_express/static/src/js/**/*.js",
        ],
    },
}
