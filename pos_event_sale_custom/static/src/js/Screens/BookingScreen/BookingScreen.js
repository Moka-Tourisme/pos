odoo.define('pos_event_sale_custom.BookingScreen', function (require) {
    'use strict';

    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const {useListener} = require("@web/core/utils/hooks");
    const {parse} = require('web.field_utils');
    const {_lt} = require('@web/core/l10n/translation');

    const {onMounted, onWillUnmount, useState} = owl;

    class BookingScreen extends PosComponent {
        setup() {
            super.setup();
            useListener('update-selected-orderline', this._updateSelectedOrderline);
            useListener('select-line', this._selectLine);
            useListener('set-numpad-mode', this._setNumpadMode);
            useListener('close-screen', this._onCloseScreen);
            useListener('click-partner', this.onClickPartner);
            useListener('click-backToOrder', this._onClickBackToOrder);
            this._state = this.env.pos.TICKET_SCREEN_STATE;
            this.state = {
                showSearchBar: !this.env.isMobile,
                selectedEvent: null,
            };
            const defaultUIState = this.props.reuseSavedUIState
                ? this._state.ui
                : {
                    selectedSyncedOrderId: null,
                    searchDetails: this.env.pos.getDefaultSearchDetails(),
                    filter: null,
                    selectedOrderlineIds: {},
                };
            Object.assign(this._state.ui, defaultUIState, this.props.ui || {});
            NumberBuffer.use({
                nonKeyboardInputEvent: 'numpad-click-input',
                triggerAtInput: 'update-selected-orderline',
                useWithBarcode: true,
            });
            console.log("this.props", this.props)
        }

        set_partner(partner) {
            this.assert_editable();
            this.partner = partner;
        }

        get partner() {
            return this.currentOrder ? this.currentOrder.get_partner() : null;
        }

        _setNumpadMode(event) {
            const {mode} = event.detail;
            NumberBuffer.capture();
            NumberBuffer.reset();
            this.env.pos.numpadMode = mode;
        }

        _selectLine() {
            NumberBuffer.reset();
        }

        async _updateSelectedOrderline(event) {
            console.log("event.detail", event.detail)
            const order = this.env.pos.get_order();
            const selectedLine = order.get_selected_orderline();
            // This validation must not be affected by `disallowLineQuantityChange`
            if (selectedLine && selectedLine.isTipLine() && this.env.pos.numpadMode !== "price") {
                /**
                 * You can actually type numbers from your keyboard, while a popup is shown, causing
                 * the number buffer storage to be filled up with the data typed. So we force the
                 * clean-up of that buffer whenever we detect this illegal action.
                 */
                NumberBuffer.reset();
                if (event.detail.key === "Backspace") {
                    this._setValue("remove");
                } else {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t("Cannot modify a tip"),
                        body: this.env._t("Customer tips, cannot be modified directly"),
                    });
                }
            } else if (this.env.pos.numpadMode === 'quantity' && this.env.pos.disallowLineQuantityChange()) {
                if (!order.orderlines.length)
                    return;
                let orderlines = order.orderlines;
                let lastId = orderlines.length !== 0 && orderlines.at(orderlines.length - 1).cid;
                let currentQuantity = this.env.pos.get_order().get_selected_orderline().get_quantity();

                if (selectedLine.noDecrease) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Invalid action'),
                        body: this.env._t('You are not allowed to change this quantity'),
                    });
                    return;
                }
                const parsedInput = event.detail.buffer && parse.float(event.detail.buffer) || 0;
                console.log("lastId", lastId)
                console.log("selectedLine.cid", selectedLine.cid)
                console.log("currentQuantity", currentQuantity)
                console.log("parsedInput", parsedInput)
                if (lastId != selectedLine.cid)
                    this._showDecreaseQuantityPopup();
                else if (currentQuantity < parsedInput)
                    this._setValue(event.detail.buffer);
                else if (parsedInput < currentQuantity)
                    this._showDecreaseQuantityPopup();
            } else {
                let {buffer} = event.detail;
                let val = buffer === null ? 'remove' : buffer;
                this._setValue(val);
                if (val == 'remove') {
                    NumberBuffer.reset();
                    this.env.pos.numpadMode = 'quantity';
                }
            }
        }

        _setValue(val) {
            if (this.currentOrder.get_selected_orderline()) {
                if (this.env.pos.numpadMode === 'quantity') {
                    const result = this.currentOrder.get_selected_orderline().set_quantity(val);
                    if (!result) NumberBuffer.reset();
                } else if (this.env.pos.numpadMode === 'discount') {
                    this.currentOrder.get_selected_orderline().set_discount(val);
                } else if (this.env.pos.numpadMode === 'price') {
                    var selected_orderline = this.currentOrder.get_selected_orderline();
                    selected_orderline.price_manually_set = true;
                    selected_orderline.set_unit_price(val);
                }
            }
        }

        async _showDecreaseQuantityPopup() {
            const {confirmed, payload: inputNumber} = await this.showPopup('NumberPopup', {
                startingValue: 0,
                title: this.env._t('Set the new quantity'),
            });
            let newQuantity = inputNumber && inputNumber !== "" ? parse.float(inputNumber) : null;
            if (confirmed && newQuantity !== null) {
                let order = this.env.pos.get_order();
                let selectedLine = this.env.pos.get_order().get_selected_orderline();
                let currentQuantity = selectedLine.get_quantity()
                if (selectedLine.is_last_line() && currentQuantity === 1 && newQuantity < currentQuantity)
                    selectedLine.set_quantity(newQuantity);
                else if (newQuantity >= currentQuantity)
                    selectedLine.set_quantity(newQuantity);
                else {
                    let newLine = selectedLine.clone();
                    let decreasedQuantity = currentQuantity - newQuantity
                    newLine.order = order;

                    newLine.set_quantity(-decreasedQuantity, true);
                    order.add_orderline(newLine);
                }
                return true;
            }
            return false;
        }


        getSelectedSyncedOrder() {
            if (this._state.ui.filter == 'SYNCED') {
                console.log("this._state.ui.selectedSyncedOrderId", this._state.ui.selectedSyncedOrderId)
                return this.props.order
            } else {
                return null;
            }
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        async onClickPartner() {
            // IMPROVEMENT: This code snippet is very similar to selectPartner of PaymentScreen.
            const currentPartner = this.currentOrder.get_partner();
            if (currentPartner && this.currentOrder.getHasRefundLines()) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t("Can't change customer"),
                    body: _.str.sprintf(
                        this.env._t(
                            "This order already has refund lines for %s. We can't change the customer associated to it. Create a new order for the new customer."
                        ),
                        currentPartner.name
                    ),
                });
                return;
            }
            const {confirmed, payload: newPartner} = await this.showTempScreen(
                'PartnerListScreen',
                {partner: currentPartner}
            );
            if (confirmed) {
                this.currentOrder.set_partner(newPartner);
                this.currentOrder.updatePricelist(newPartner);
            }
        }

        async _onClickBackToOrder() {
            await this.showScreen('ProductScreen');
        }

        async _onCloseScreen() {
            await this.showScreen('ProductScreen');
        }

    }

    BookingScreen.template = 'BookingScreen';
    Registries.Component.add(BookingScreen);
    BookingScreen.numpadActionName = _lt('Validate');

    return BookingScreen;
});