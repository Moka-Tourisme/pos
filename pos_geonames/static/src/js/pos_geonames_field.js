odoo.define("pos_geonames_field.ClientDetailsEditInherit", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const { _t } = require("web.core");
    const { getDataURLFromFile } = require('web.utils');
    const Registries = require('point_of_sale.Registries');
    var ClientDetailsEdit = require("point_of_sale.ClientDetailsEdit");

    var ClientDetailsEditInherit = (ClientDetailsEdit) => class extends ClientDetailsEdit {
        constructor() {
            super(...arguments);
            $(document).ready(function () {
                $(".client-address-autocomplete").select2();
            });
        }

        captureChange(event) {
            let country_id_before = parseInt(this.changes.country_id);
            this.changes[event.target.name] = event.target.value;
            if (country_id_before !== parseInt(this.changes.country_id)) {
                $('.client-address-states').empty();
                $('.client-address-states').append(new Option("None", ""))
                this.env.pos.states.forEach((state) => {
                    if (state.country_id[0] === parseInt(this.changes.country_id)) {
                        $('.client-address-states').append(new Option(state.name, state.id))
                    }
                })
            }
        }
    };

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditInherit);
    return ClientDetailsEdit;
})