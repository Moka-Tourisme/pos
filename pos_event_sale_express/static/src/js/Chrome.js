odoo.define("pos_event_sale_express.Chrome", function (require) {
    "use strict";
    const {posbus} = require('point_of_sale.utils');
    const {useBus} = require("@web/core/utils/hooks");

    const Chrome = require("point_of_sale.Chrome");
    const Registries = require('point_of_sale.Registries');


    const UpdatedChrome = Chrome => class extends Chrome {

        constructor() {
            super(...arguments);
            useBus(posbus, 'open-event-selector-popup', this.showEventSelectorPopup);
        }

        async showEventSelectorPopup() {
            if (this.env.pos.config.iface_event_shop_express) {
                console.log('Events today', this.env.pos.db.events_today)
                if (this.env.pos.db.events_today.length === 1) {
                    if (this.env.pos.config.iface_time_before_event && this.env.pos.config.iface_time_before_event !== 0) {
                        let event_date_begin = moment(this.env.pos.db.events_today[0].date_begin).subtract(this.env.pos.config.iface_time_before_event, 'minutes')
                        if (event_date_begin.isBefore(moment())) {
                            this.showPopup("EventTicketsPopup", {
                                event: this.env.pos.db.events_today[0],
                            });
                        } else {
                            setTimeout(() => {
                                posbus.trigger('open-event-selector-popup')
                            }, 30000)
                        }
                    } else {
                        this.showPopup("EventTicketsPopup", {
                            event: this.env.pos.db.events_today[0],
                        });
                    }
                } else if (this.env.pos.db.events_today.length > 1) {
                    console.log('Oui')
                    let events_today_filtered = []
                    if (this.env.pos.config.iface_time_before_event && this.env.pos.config.iface_time_before_event !== 0) {
                        console.log('Time before event', this.env.pos.config.iface_time_before_event)
                        //     For each events_today, remove iface_time_before_event minutes from date_begin and if the result is before moment() then keep the event in events_today if not remove it
                        this.env.pos.db.events_today.forEach((event) => {
                            let event_date_begin = moment(event.date_begin).subtract(this.env.pos.config.iface_time_before_event, 'minutes')
                            console.log('Event date begin', event_date_begin.toLocaleString())
                            console.log('Moment', moment().toLocaleString())
                            console.log('Is after', moment().isAfter(event_date_begin))
                            if (moment().isAfter(event_date_begin)) {
                                // Remove the event from events_today array
                                events_today_filtered.push(event)
                            }
                        })
                        console.log('Events today filtered', events_today_filtered)
                        if (events_today_filtered.length === 1) {
                            console.log("ICI")
                            this.showPopup("EventTicketsPopup", {
                                event: events_today_filtered[0],
                            });
                        } else if (events_today_filtered.length > 1) {
                            this.showPopup("EventSelectorPopup", {});
                        } else {
                            setTimeout(() => {
                                posbus.trigger('open-event-selector-popup')
                            }, 30000)
                        }
                    } else {
                        this.showPopup("EventSelectorPopup", {});
                    }
                }
            }
        }
    }
    Registries.Component.extend(Chrome, UpdatedChrome);
});