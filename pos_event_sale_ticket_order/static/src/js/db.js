/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_sale_ticket_order.db", function (require) {
    "use strict";

    const PosDB = require("point_of_sale.DB");
    const rpc = require("web.rpc");
    const {_t} = require("web.core");

    PosDB.include({

        _getUpdateEventSeatsAvailableFieldsEventTicket: function () {
            return ["id", "seats_limited", "seats_available", "sequence"];
        },

        /**
         * Adds or updates event tickets loaded in the PoS.
         * This method is called on startup, and when updating the event availability.
         * It keeps the access map up-to-date, and computes some fields.
         *
         * @param {Array} tickets
         */
        addEventTickets: function (tickets) {
            console.log("addEventTickets");
            /* eslint-disable no-param-reassign */
            if (!(tickets instanceof Array)) {
                tickets = [tickets];
            }
            for (const ticket of tickets) {
                // Sanitize seats_available and seats_max for unlimited tickets
                // This avoids checking for seats_limited every time.
                if (!ticket.seats_limited) {
                    ticket.seats_max = Infinity;
                    ticket.seats_available = Infinity;
                }
                // Add or update local record
                // Use object.assign to update current Object, if it already exists
                if (this.event_ticket_by_id[ticket.id]) {
                    Object.assign(this.event_ticket_by_id[ticket.id], ticket);
                } else {
                    // Ignore ticket updates with missing fields.
                    // This can happen during the seats availability update.
                    if (!ticket.event_id) {
                        continue;
                    }
                    // Map event ticket by id
                    this.event_ticket_by_id[ticket.id] = ticket;
                    // Map event ticket by event id
                    if (!this.event_ticket_by_event_id[ticket.event_id[0]]) {
                        this.event_ticket_by_event_id[ticket.event_id[0]] = [];
                    }
                    this.event_ticket_by_event_id[ticket.event_id[0]].push(ticket);
                    // Order tickets by sequence
                    this.event_ticket_by_event_id[ticket.event_id[0]].sort(function (a, b) {
                        return a['sequence'] - b['sequence'];
                    });
                    console.log("New ticket", this.event_ticket_by_event_id)
                    // Map event ticket by product id
                    if (!this.event_ticket_by_product_id[ticket.product_id[0]]) {
                        this.event_ticket_by_product_id[ticket.product_id[0]] = [];
                    }
                    this.event_ticket_by_product_id[ticket.product_id[0]].push(ticket);
                }
            }
            Object.values(this.event_ticket_by_event_id).forEach(function (event) {
                // Order tickets by sequence
                event.sort(function (a, b) {
                    return a['sequence'] - b['sequence'];
                });
            })
        },
    });

    return PosDB;
});
