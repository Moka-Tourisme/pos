# @author Duciel Romain <romain@mokatourisme.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Point of sale customer required",
    "summary": "Require a customer on POS orders",
    "website": "https://github.com/OCA/pos",
    "category": "Marketing",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "views/res_config_settings.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_customer_required/static/src/js/**/*.js",
            "pos_customer_required/static/src/scss/**/*.scss",
            "pos_customer_required/static/src/xml/**/*.xml",
        ],
    },
}
