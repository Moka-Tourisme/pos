# @author Duciel Romain <romain@mokatourisme.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Point of sale product require customer",
    "summary": "Require customer on product",
    "website": "https://github.com/OCA/pos",
    "category": "Marketing",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "views/product_template.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_product_require_customer/static/src/js/**/*.js",
            "pos_product_require_customer/static/src/scss/**/*.scss",
            "pos_product_require_customer/static/src/xml/**/*.xml",
        ],
    },
}