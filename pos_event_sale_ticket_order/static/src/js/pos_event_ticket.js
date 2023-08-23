odoo.define('pos_event_sale_ticket_order.pos_event_tickets', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_models([
        {
            model: "event.event.ticket",
            after: "event.event",
            label: "Event Tickets",
            fields: [
                "name",
                "description",
                "event_id",
                "product_id",
                "price",
                "seats_limited",
                "seats_available",
                "sequence",
            ],
            condition: function (self) {
                return self.config.iface_event_sale;
            },
            domain: function (self) {
                const event_ids = Object.keys(self.db.event_by_id).map((id) => Number(id));
                return [
                    ["product_id.active", "=", true],
                    ["available_in_pos", "=", true],
                    ["event_id", "in", event_ids],
                ];
            },
            loaded: function (self, records) {
                records.sort((a, b) => a.sequence - b.sequence); // Sort event tickets by sequence
                self.db.addEventTickets(
                    records.map((record) => {
                        record.pos = self;
                        return new models.EventTicket({}, record);
                    })
                );
            },
        },
    ]);

    console.log(models)
    return models;
});
