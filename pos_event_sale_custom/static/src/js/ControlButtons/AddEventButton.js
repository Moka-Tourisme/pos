odoo.define("pos_event_sale_custom.AddEventButton", function (require) {
    "use strict";

    const AddEventButton = require("pos_event_sale.AddEventButton");
    const Registries = require('point_of_sale.Registries');

    const AddEventButtonInherited = (AddEventButton) =>
        class extends AddEventButton {
            async onClick() {
                await this.showScreen("BookingScreen", {
                    ui: {filter: 'SYNCED'},
                    order: this.env.pos.get_order(),
                });
            }
        };
    Registries.Component.extend(AddEventButton, AddEventButtonInherited);
    return AddEventButton;
});

