/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_sale_express.db", function (require) {
    "use strict";

    const PosDB = require("point_of_sale.DB");
    const rpc = require("web.rpc");
    const {_t} = require("web.core");

    PosDB.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.events_today = [];
        },

        addEventsToday: function (events) {
            if (!(events instanceof Array)) {
                events = [events];
            }
            for (const event of events) {
                if (event.date_begin) {
                    event.date_begin = moment.utc(event.date_begin).toDate();
                }
                if (event.date_end) {
                    event.date_end = moment.utc(event.date_end).toDate();
                }
                if (this.events_today[event.id]) {
                    Object.assign(this.event_today[event.id], event);
                } else {
                    this.events_today.push(event);
                }
            }
        },
    });

    return PosDB;
});
