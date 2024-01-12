
odoo.define('pos_event_sale_custom.CalendarScreen', function (require) {
    'use strict';


    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { Component, useState } = owl;

    class CalendarScreen extends PosComponent {

        constructor() {
            super(...arguments);
            this.state = useState({ value: this.props.value });
        }
    }

    CalendarScreen.template = 'CalendarScreen';
    Registries.Component.add(CalendarScreen);

    return CalendarScreen;
});