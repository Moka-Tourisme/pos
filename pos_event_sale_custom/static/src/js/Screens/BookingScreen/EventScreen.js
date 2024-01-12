
odoo.define('pos_event_sale_custom.EventScreen', function (require) {
    'use strict';


    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { Component, useState } = owl;

    class EventScreen extends PosComponent {

        constructor() {
            super(...arguments);
            this.state = useState({ value: this.props.value });
        }
    }

    EventScreen.template = 'EventScreen';
    Registries.Component.add(EventScreen);

    return EventScreen;
});