odoo.define("pos_customer_required.PartnerDetailsEdit", function (require) {
    "use strict";
    const PartnerDetailsEdit = require("point_of_sale.PartnerDetailsEdit");

    const {_t} = require("web.core");
    const {getDataURLFromFile} = require("web.utils");
    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");

    const OverloadPartnerDetailsEdit = (PartnerDetailsEdit) =>
        class OverloadPartnerDetailsEdit extends PartnerDetailsEdit {

            missingCustomerFields(customer) {
                if (!customer || this.env.pos.config.res_partner_required_fields_names === "") {
                    return [];
                }
                return this.env.pos.config.res_partner_required_fields_names.split(",").filter(
                    (field) => !customer[field]
                );
            }

            saveChanges() {
                const processedChanges = {};
                for (const [key, value] of Object.entries(this.changes)) {
                    if (this.intFields.includes(key)) {
                        processedChanges[key] = parseInt(value) || false;
                    } else {
                        processedChanges[key] = value;
                    }
                }

                // Validate state_id and country_id
                if (
                    processedChanges.state_id &&
                    this.env.pos.states.find((state) => state.id === processedChanges.state_id)
                        .country_id[0] !== processedChanges.country_id
                ) {
                    processedChanges.state_id = false;
                }

                // Merge processedChanges into the current partner data
                const partnerData = {...this.props.partner, ...processedChanges};

                // Check for missing required customer fields
                const missingFields = this.missingCustomerFields(partnerData);

                if (missingFields.length > 0) {
                    return this.showPopup("ErrorPopup", {
                        title: _t("Missing Customer Fields"),
                        body: _t(
                            `The following fields are required: ${missingFields.join(", ")}`
                        ),
                    });
                }

                // Check for required name
                if (!partnerData.name || partnerData.name.trim() === "") {
                    return this.showPopup("ErrorPopup", {
                        title: _t("A Customer Name Is Required"),
                    });
                }

                // Add partner ID and trigger save
                processedChanges.id = this.props.partner.id || false;
                this.trigger("save-changes", {processedChanges});
            }
        }
    Registries.Component.extend(PartnerDetailsEdit, OverloadPartnerDetailsEdit);
    return PartnerDetailsEdit;
});
