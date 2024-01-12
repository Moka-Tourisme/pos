odoo.define('pos_event_sale_custom.TicketsScreen', function (require) {
    'use strict';


    const PosComponent = require('point_of_sale.PosComponent');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const {Component, useState} = owl;
    const {useListener} = require("@web/core/utils/hooks");
    const Registries = require("point_of_sale.Registries");

    class TicketsScreen extends IndependentToOrderScreen {

        /**
         * @param {Object} props
         * @param {Object} props.event
         */
        setup() {
            super.setup();
            useListener("click-event-ticket", this._clickEventTicket);
        }

        get title() {
            return this.props.event.name;
        }

        get eventTicketsToDisplay() {
            if (this.props.event) {
                return this.props.event.getEventTickets();
            }
            return [];
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        getSelectedSyncedOrder() {
            if (this._state.ui.filter == 'SYNCED') {
                return this._state.syncedOrders.cache[this._state.ui.selectedSyncedOrderId];
            } else {
                return null;
            }
        }
        getSelectedOrderlineId() {
            return this._state.ui.selectedOrderlineIds[this._state.ui.selectedSyncedOrderId];
        }

        _getAddProductOptions(eventTicket) {
            return eventTicket._prepareOrderlineOptions();
        }

        _clickEventTicket(ev) {
            const eventTicket = ev.detail;
            console.log("ICI click event ticket")
            console.log("this.props.event", this.props.event)
            console.log("ev", ev)
            console.log("this.props.event", this.props.ev)
            console.log("this", this)
            console.log("this.env", this.env)
            console.log("this.env.pos", this.env.pos)
            if (!this.currentOrder) {
                this.env.pos.add_new_order();
            }
            const product = eventTicket.getProduct();
            const options = this._getAddProductOptions(eventTicket);
            if (!options) {
                return;
            }
            this.currentOrder.add_product(product, options);
        }


    }

    TicketsScreen.template = 'TicketsScreen';
    Registries.Component.add(TicketsScreen);

    return TicketsScreen;
});