odoo.define("pos_customer_required.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");

    // eslint-disable-next-line no-shadow
    const OverloadPaymentScreen = (PaymentScreen) =>
        // eslint-disable-next-line no-shadow
        class OverloadPaymentScreen extends PaymentScreen {
            async _isOrderValid() {
                // Check if the customer is set and required in pos.config
                const posConfig = this.env.pos.config;
                const partner = this.env.pos.get_order().get_partner();

                if (posConfig.iface_customer_required && !partner) {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t("Customer Required"),
                        body: this.env._t("Please select a customer."),
                    });
                    return false;
                }

                return await super._isOrderValid(...arguments);
            }
        };

    Registries.Component.extend(PaymentScreen, OverloadPaymentScreen);

    return PaymentScreen;
});