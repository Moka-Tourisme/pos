/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_sale_express.models", function (require) {
    "use strict";

    const models = require("point_of_sale.models");

    models.load_models([
        {
            model: "event.event",
            after: "product.product",
            label: "Events",
            fields: [
                "name",
                "display_name",
                "event_type_id",
                "tag_ids",
                "country_id",
                "date_begin",
                "date_end",
                "date_tz",
                "seats_limited",
                "seats_available",
            ],
            condition: function (self) {
                return self.config.iface_event_shop_express;
            },
            domain: function (self) {
                const today = moment().utc().startOf("day");
                const domain = [
                    ["date_begin", "<=", today.format("YYYY-MM-DD")],
                    ["date_end", ">=", today.format("YYYY-MM-DD")],
                ];
                return domain;
            },
            loaded: function (self, records) {
                self.db.addEventsToday(
                    records.map((record) => {
                        record.pos = self;
                        return new models.EventEvent({}, record);
                    })
                );
            },
        },
    ]);

    return models;
});
