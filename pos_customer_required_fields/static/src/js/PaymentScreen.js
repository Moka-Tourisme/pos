odoo.define("pos_customer_required_fields.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");

    // eslint-disable-next-line no-shadow
    const OverloadPaymentScreen = (PaymentScreen) =>
        // eslint-disable-next-line no-shadow
        class OverloadPaymentScreen extends PaymentScreen {

            missingCustomerFields() {
                const customer = this.env.pos.get_order().get_partner();
                if(!customer || this.env.pos.config.res_partner_required_fields_names === "")
                {
                    return [];
                }
                return this.env.pos.config.res_partner_required_fields_names.split(",").filter(
                    function(name) {
                        return !customer[name];
                    }
                )
            }
            async _isOrderValid() {
                const missingFields = this.missingCustomerFields();
                if(missingFields.length > 0) {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t("Customer Required"),
                        body: this.env._t("Please fill in the following fields: ") + missingFields.join(", "),
                    });
                    return false;
                }

                return await super._isOrderValid(...arguments);
            }
        };

    Registries.Component.extend(PaymentScreen, OverloadPaymentScreen);

    return PaymentScreen;
});