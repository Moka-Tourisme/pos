odoo.define("pos_geonames_field.ClientDetailsEditInherit", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require('point_of_sale.Registries');
    const ClientDetailsEdit = require("point_of_sale.ClientDetailsEdit");
    const {useState, useRef} = owl.hooks;
    const rpc = require('web.rpc');


    const ClientDetailsEditInherit = (ClientDetailsEdit) => class extends ClientDetailsEdit {
        constructor() {
            super(...arguments);
            this.inputAutocomplete = useRef('inputAutocomplete');
        }

        mounted() {
            this.choices = new Choices(this.inputAutocomplete.el, {
                allowHTML: true,
                searchEnabled: true,
                searchResultLimit: 25
            });
            this.choices.input.element.addEventListener('keyup', this._updateCountryList.bind(this));
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

        _updateStatesList(data) {
            let country_id_before = parseInt(this.changes.country_id);
            this.changes.country_id = data;
            this.el.getElementsByClassName("client-address-country")[0].value = data;
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

        /**
         * @private
         * @param {KeyBoardEvent} ev
         */
        async _updateCountryList(ev) {
            const query = this.choices.input.element.value;
            const data = await rpc.query({
                model: 'res.city.zip',
                method: 'search_read',
                kwargs: {
                    fields: ['id', 'display_name', 'name', 'city_id', 'country_id', 'state_id'],
                    domain: [
                        ['display_name', 'ilike', query]
                    ],
                    limit: 25
                }
            })

            const countries = data.map((rec) => {
                return {
                    value: rec.id,
                    label: rec.display_name,
                    customProperties: {
                        zip: rec.name,
                        state: rec.state_id[0],
                        country: rec.country_id[0],
                        city: rec.city_id[1]
                    }
                }
            });

            this.choices.setChoices(countries, 'value', 'label', true);
        }

        async _updateChanges() {
            const data = this.choices.getValue().customProperties;
            await this._updateStatesList(data.country)
            this.el.getElementsByClassName("client-address-states")[0].value = data.state;
            this.el.getElementsByClassName("client-address-city")[0].value = data.city;
            this.el.getElementsByClassName("client-address-zip")[0].value = data.zip;
        }
    };

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditInherit);
    return ClientDetailsEdit;
})