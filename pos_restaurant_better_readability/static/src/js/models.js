odoo.define("pos_restaurant_custom_ticket.models", function (require) {
    "use strict";

    const models = require("point_of_sale.models");

    models.Orderline = models.Orderline.extend({
        get_full_product_name: function () {
            if (this.full_product_name) {
                return this.full_product_name
            }
            var full_name = this.product.display_name;
            if (this.description) {
                full_name += ` (${this.description})`;
            }
            return full_name;
        },
        generate_wrapped_product_name: function () {
            var MAX_LENGTH = 24; // 40 * line ratio of .6
            var wrapped = [];
            var name = this.product.display_name;
            var caracteristics = this.get_full_product_name();
            var current_line_name = "";
            var current_line_caracteristics = "";

            caracteristics = caracteristics.replace(name, "").replace("(", "").replace(")", "");
            if (caracteristics.indexOf(" ") === 0) {
                caracteristics = caracteristics.slice(1);
            }
            if (caracteristics.indexOf(name) === 0) {
                caracteristics = caracteristics.slice(name.length);
            }

            while (name.length > 0) {
                var space_index = name.indexOf(" ");

                if (space_index === -1) {
                    space_index = name.length;
                }

                if (current_line_name.length + space_index > MAX_LENGTH) {
                    if (current_line_name.length) {
                        wrapped.push(current_line_name);
                    }
                    current_line_name = "";
                }

                current_line_name += name.slice(0, space_index + 1);
                name = name.slice(space_index + 1);
            }

            if (current_line_name.length) {
                wrapped.push(current_line_name);
            }

            while (caracteristics.length > 0) {
                var space_index = caracteristics.indexOf(" ");

                if (space_index === -1) {
                    space_index = caracteristics.length;
                }

                if (current_line_caracteristics.length + space_index > MAX_LENGTH) {
                    if (current_line_caracteristics.length) {
                        wrapped.push(current_line_caracteristics);
                    }
                    current_line_caracteristics = "";
                }

                current_line_caracteristics += caracteristics.slice(0, space_index + 1);
                caracteristics = caracteristics.slice(space_index + 1);
            }

            if (current_line_caracteristics.length) {
                wrapped.push(current_line_caracteristics);
            }
            return wrapped;
        },
    });

});