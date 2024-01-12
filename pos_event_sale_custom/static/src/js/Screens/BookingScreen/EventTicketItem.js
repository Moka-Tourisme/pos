/*
    Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_sale_custom.EventTicketItem", function (require) {
    "use strict";

    const {useState} = owl;
    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");
    const {onWillRender} = owl;

    class EventTicketItem extends PosComponent {
        /**
         * @param {Object} props
         * @param {Object} props.eventTicket
         */
        setup() {
            super.setup();
            this.state = useState({
                orderedQty: this.props.eventTicket.getOrderedQuantity(),
                seatsAvailable: this.props.eventTicket.getSeatsAvailableReal(),
            });
            onWillRender(this.willRendered);
        }

        willRendered() {
            this._updateQuantities();
        }

        get imageUrl() {
            const product_id = this.props.eventTicket.product_id[0];
            const product = this.env.pos.db.get_product_by_id(product_id);
            return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
        }

        get pricelist() {
            const current_order = this.env.pos.get_order();
            if (current_order) {
                return current_order.pricelist;
            }
            return this.env.pos.default_pricelist;
        }

        get price() {
            const eventTicket = this.props.eventTicket;
            return eventTicket
                .getProduct()
                .get_price(this.pricelist, 1, eventTicket.getPriceExtra());
        }

        get priceFormatted() {
            return this.env.pos.format_currency(this.price, "Product Price");
        }

        get disabled() {
            return this.state.seatsAvailable <= 0;
        }

        get addedClasses() {
            return {
                disabled: this.disabled,
            };
        }

        clickEventTicket() {
            if (!this.disabled) {
                this.trigger("click-event-ticket", this.props.eventTicket);
            }
        }

        _updateQuantities() {
            this.state.seatsAvailable = this.props.eventTicket.getSeatsAvailableReal();
            this.state.orderedQty = this.props.eventTicket.getOrderedQuantity();
        }
    }

    EventTicketItem.template = "EventTicketItem";

    Registries.Component.add(EventTicketItem);
    return EventTicketItem;
});
