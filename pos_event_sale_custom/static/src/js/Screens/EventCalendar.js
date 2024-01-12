odoo.define("pos_event_sale_custom.EventCalendar", function (require) {

    "use strict";

    const {useState} = owl;
    const Registries = require("point_of_sale.Registries");

    const PosComponent = require('point_of_sale.PosComponent');
    const EventCalendar = require('pos_event_sale.EventCalendar');

    const EventCalendarCustom = (EventCalendar) =>
        class extends EventCalendar {

            _getCalendarOptions() {
                const calendarOptions = super._getCalendarOptions();
                console.log("calendarOptions", calendarOptions)
                calendarOptions.header = {
                    left: "prev",
                    center: "title",
                    right: "next",
                };
                calendarOptions.firstDay = moment.localeData().firstDayOfWeek();
                calendarOptions.weekNumbers = true;
                calendarOptions.weekText = "#";
                return calendarOptions;
            }

        };

    Registries.Component.extend(EventCalendar, EventCalendarCustom);
    return EventCalendar;
});