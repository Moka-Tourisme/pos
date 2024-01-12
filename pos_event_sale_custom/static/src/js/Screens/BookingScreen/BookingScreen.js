odoo.define('pos_event_sale_custom.BookingScreen', function (require) {
    'use strict';

    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const {useListener} = require("@web/core/utils/hooks");
    const {_lt} = require('@web/core/l10n/translation');

    const {onMounted, onWillUnmount, useState} = owl;

    class BookingScreen extends PosComponent {
        setup() {
            super.setup();
            useListener('close-screen', this._onCloseScreen);
            useListener('click-order-line', this._onClickOrderline);
            useListener('click-partner', this.onClickPartner);
            useListener('click-pay', this._onClickPay);
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
            console.log("this.props", this.props)
        }

        set_partner(partner) {
            this.assert_editable();
            this.partner = partner;
        }

        get_partner() {
            return this.partner;
        }

        getSelectedSyncedOrder() {
            if (this._state.ui.filter == 'SYNCED') {
                console.log("this._state.ui.selectedSyncedOrderId", this._state.ui.selectedSyncedOrderId)
                return this.props.order
            } else {
                return null;
            }
        }

        getSelectedOrderlineId() {
            console.log("TEST ICI ")
            console.log("state.ui.selectedOrderlineIds", this._state.ui.selectedOrderlineIds)
            return this._state.ui.selectedOrderlineIds[this._state.ui.selectedSyncedOrderId];
        }

        _onClickOrderline({detail: orderline}) {
            const order = this.getSelectedSyncedOrder();
            console.log("order", order)
            this._state.ui.selectedOrderlineIds[order.backendId] = orderline.id;
            console.log("this._state.ui.selectedOrderlineIds", this._state.ui.selectedOrderlineIds)
            NumberBuffer.reset();
        }

        get currentOrder() {
            console.log("PASSAGE ICI currentOrder")
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

        async _onClickPay() {
            if (this.env.pos.get_order().orderlines.some(line => line.get_product().tracking !== 'none' && !line.has_valid_product_lot()) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                const {confirmed} = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Some Serial/Lot Numbers are missing'),
                    body: this.env._t('You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?'),
                    confirmText: this.env._t('Yes'),
                    cancelText: this.env._t('No')
                });
                if (confirmed) {
                    this.showScreen('PaymentScreen');
                }
            } else {
                this.showScreen('PaymentScreen');
            }
        }

        _onCloseScreen() {
            this.close();
        }

    }

    BookingScreen.template = 'BookingScreen';
    Registries.Component.add(BookingScreen);
    BookingScreen.numpadActionName = _lt('Payment');

    return BookingScreen;
});