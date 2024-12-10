odoo.define("pos_product_require_customer.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");

    // eslint-disable-next-line no-shadow
    const OverloadPaymentScreen = (PaymentScreen) =>
        // eslint-disable-next-line no-shadow
        class OverloadPaymentScreen extends PaymentScreen {
            // Check if there is a product that requires a customer in all the order lines
            hasCustomerRequiredProduct() {
                return this.env.pos.get_order().get_orderlines().some((line) => {
                    return line.product.require_customer;
                });
            }

            async _isOrderValid() {
                const hasCustomerRequiredProduct = this.hasCustomerRequiredProduct();
                console.log('hasCustomerRequiredProduct', hasCustomerRequiredProduct);
                if (hasCustomerRequiredProduct) {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t("Customer Required"),
                        body: this.env._t("Please add a customer to the order before proceeding."),
                    });
                    return false;
                }
                return super._isOrderValid();
            }
        }
    Registries.Component.extend(PaymentScreen, OverloadPaymentScreen);

    return PaymentScreen;
});
