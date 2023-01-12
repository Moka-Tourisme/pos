{
    "name": "PoS Geonames",
    "summary": "PoS Geonames",
    "author": "Moka Tourisme",
    "website": "https://www.mokatourisme.fr",
    "category": "Others",
    "version": "15.0.1",
    "license": "AGPL-3",
    "assets": {
        "point_of_sale.assets": [
            "pos_geonames/static/src/js/*",
            "pos_geonames/static/lib/choices.js",
            "pos_geonames/static/lib/choices.css",
        ],
        "web.assets_qweb": [
            "pos_geonames/static/src/xml/*",
        ],
    },
    "depends": [
        "point_of_sale",
        "base_location",
    ],
}
