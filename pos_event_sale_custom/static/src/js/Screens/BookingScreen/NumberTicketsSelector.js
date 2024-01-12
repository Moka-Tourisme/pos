
odoo.define('pos_event_sale_custom.NumberTicketsSelector', function (require) {
    'use strict';


    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { Component, useState } = owl;

    class NumberTicketsSelector extends PosComponent {

        constructor() {
            super(...arguments);
            this.state = useState({ value: this.props.value });
        }
    }

    NumberTicketsSelector.template = 'NumberTicketsSelector';
    Registries.Component.add(NumberTicketsSelector);

    return NumberTicketsSelector;
});