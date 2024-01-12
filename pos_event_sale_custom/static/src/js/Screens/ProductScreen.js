/*
    Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_sale_custom.ProductScreen", function (require) {
    "use strict";

    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");

    const PosEventSaleCustomProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _clickProduct(event) {
                const product = event.detail;
                if (
                    this.env.pos.config.iface_event_sale &&
                    product.detailed_type === "event"
                ) {
                    return this.showScreen("BookingScreen", {
                        ui: {filter: 'SYNCED'},
                        order: this.env.pos.get_order(),
                    });
                }
                return super._clickProduct(event);
            }
        };

    Registries.Component.extend(ProductScreen, PosEventSaleCustomProductScreen);
    return ProductScreen;
});
