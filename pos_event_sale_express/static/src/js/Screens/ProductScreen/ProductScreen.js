odoo.define("pos_event_sale_express.ProductScreen", function (require) {
    "use strict";

    const ProductScreen = require("pos_event_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");
    const {posbus} = require('point_of_sale.utils');


    const UpdatedProductScreen = ProductScreen => class extends ProductScreen {
        mounted() {
            super.mounted(...arguments);
            // How to trigger the popup every minute
            posbus.trigger('open-event-selector-popup')
        }
    }
    Registries.Component.extend(ProductScreen, UpdatedProductScreen);
});