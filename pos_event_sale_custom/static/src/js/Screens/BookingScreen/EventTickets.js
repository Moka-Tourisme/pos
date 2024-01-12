/*
    Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_sale_custom.EventTickets", function (require) {
    "use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const {useListener} = require("@web/core/utils/hooks");
    const Registries = require("point_of_sale.Registries");

    class EventTickets extends PosComponent {
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
            return this.props.event.getEventTickets();
        }
        get currentOrder() {
            console.log("PASSAGE ICI currentOrder")
            return this.env.pos.get_order();
        }
        _getAddProductOptions(eventTicket) {
            return eventTicket._prepareOrderlineOptions();
        }
        _clickEventTicket(ev) {
            const eventTicket = ev.detail;
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
    EventTickets.template = "EventTicketsPopup";

    Registries.Component.add(EventTickets);
    return EventTickets;
});
