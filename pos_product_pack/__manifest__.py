# Copyright 2021 ACSONE SA/NV
# Contributors : Damien Horvat <damien@moka.cloud>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pos Product Pack",
    "summary": """
        Allows to sell product packs on POS sessions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA), Moka",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/product-pack",
    "depends": [
        "product_pack",
        "point_of_sale",
    ],
    "data": [],
    "assets": {
        "point_of_sale.assets": [
            "pos_product_pack/static/src/js/models.js",
        ],
    },
    "installable": True,
}
