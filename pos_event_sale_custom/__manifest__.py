{
    "name": "Point of Sale Events Custom",
    "summary": "Sell events from Point of Sale",
    "author": "MokaTourisme, Odoo Community Association (OCA)",
    "category": "Marketing",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["pos_event_sale"],
    "data": [
    ],
    "assets": {
        "point_of_sale.assets": [
            "web/static/lib/fullcalendar/core/main.css",
            "web/static/lib/fullcalendar/daygrid/main.css",
            "web/static/lib/fullcalendar/core/main.js",
            "web/static/lib/fullcalendar/daygrid/main.js",
            "web/static/lib/fullcalendar/interaction/main.js",
            "pos_event_sale_custom/static/src/js/**/*.js",
            "pos_event_sale_custom/static/src/scss/**/*.scss",
            "pos_event_sale_custom/static/src/xml/**/*.xml",
        ],
        "web.assets_tests": [
            "pos_event_sale_custom/static/tests/tours/**/*",
        ],
    },
}