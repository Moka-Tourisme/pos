odoo.define("pos_product_pack.models", function (require) {
    "use strict";

    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const { Orderline } = require('point_of_sale.models');
    const { Order } = require('point_of_sale.models');

    const PosProductPackPosGlobalState = (PosGlobalState) => class PosProductPackPosGlobalState extends PosGlobalState {
        async _loadProductPackLines() {
            const product_pack_lines = await this.env.services.rpc({
                model: 'product.pack.line',
                method: 'search_read',
                args: [[['parent_product_id.available_in_pos', '=', true]]],
                fields: ['parent_product_id', 'quantity', 'product_id'],
            });
            
            this.product_pack_line_by_id = {};
            product_pack_lines.forEach(line => {
                this.product_pack_line_by_id[line.id] = line;
            });
        }

        async _loadProductFields() {
            const product_ids = Object.keys(this.db.product_by_id).map(id => parseInt(id));
            
            if (product_ids.length) {
                const products_data = await this.env.services.rpc({
                    model: 'product.product',
                    method: 'read',
                    args: [product_ids, ['pack_ok', 'pack_line_ids', 'pack_type', 'pack_component_price']],
                });
                
                products_data.forEach(product => {
                    const localProduct = this.db.product_by_id[product.id];
                    if (localProduct) {
                        localProduct.pack_ok = product.pack_ok;
                        localProduct.pack_line_ids = product.pack_line_ids;
                        localProduct.pack_type = product.pack_type;
                        localProduct.pack_component_price = product.pack_component_price;
                    }
                });
                
                const template_ids = [...new Set(Object.values(this.db.product_by_id)
                    .map(p => p.product_tmpl_id).filter(Boolean))];
                
                if (template_ids.length) {
                    const templates_data = await this.env.services.rpc({
                        model: 'product.template',
                        method: 'read',
                        args: [template_ids, ['pack_ok']],
                    });
                    
                    templates_data.forEach(template => {
                        Object.values(this.db.product_by_id).forEach(product => {
                            if (product.product_tmpl_id && product.product_tmpl_id === template.id) {
                                product.template_pack_ok = template.pack_ok;
                            }
                        });
                    });
                }
            }
        }

        async afterLoad() {
            await super.afterLoad(...arguments);
            await this._loadProductPackLines();
            await this._loadProductFields();
        }
    };

    Registries.Model.extend(PosGlobalState, PosProductPackPosGlobalState);

    const PosProductPackOrderline = (Orderline) => class PosProductPackOrderline extends Orderline {
        init(obj, options) {
            super.init(...arguments);
            this.pack_parent_line_id = null;
            this.pack_line_id = null;
            this.pack_child_line_ids = [];
        }

        get_pack_lines() {
            const pack_line_ids = this.get_product().pack_line_ids || [];
            const lines = [];
            for (let i = 0; i < pack_line_ids.length; i++) {
                if (this.pos.product_pack_line_by_id[pack_line_ids[i]]) {
                    lines.push(this.pos.product_pack_line_by_id[pack_line_ids[i]]);
                }
            }
            return lines;
        }
        
        get_pack_line_can_be_merged_with(pack_line) {
            let to_merge_orderline = null;
            for (let i = 0; i < this.order.get_orderlines().length; i++) {
                const current_line = this.order.get_orderlines()[i];
                if (
                    current_line.pack_line_id &&
                    current_line.pack_line_id.id === pack_line.id
                ) {
                    to_merge_orderline = current_line;
                    break;
                }
            }
            return to_merge_orderline;
        }

        remove_pack_line() {
            // Check if line is a pack one and has children
            if (this.get_product().pack_ok) {
                // The line to remove is a product pack
                // So, we remove the concerning children lines
                if (this.pack_child_line_ids && this.pack_child_line_ids.length) {
                    // Clone array to avoid modification during iteration
                    [...this.pack_child_line_ids].forEach(child_line_id => {
                        const child_line = this.order.get_orderline(child_line_id);
                        if (child_line) {
                            this.order.remove_orderline(child_line);
                        }
                    });
                }
            }
            // Check if line is a pack child, then, remove itself from
            // parent pack lines
            if (this.pack_parent_line_id) {
                const parent_line = this.order.get_orderline(
                    this.pack_parent_line_id.id || this.pack_parent_line_id
                );
                if (parent_line && parent_line.pack_child_line_ids && parent_line.pack_child_line_ids.includes(this.id)) {
                    const index = parent_line.pack_child_line_ids.indexOf(this.id);
                    parent_line.pack_child_line_ids.splice(index, 1);
                }
            }
        }

        set_pack_lines_quantity(quantity) {
            if (!this.pack_child_line_ids) {
                this.pack_child_line_ids = [];
            }
            
            if (this.get_product().pack_ok && this.pack_child_line_ids.length) {
                this.pack_child_line_ids.forEach(child_line_id => {
                    const child_line = this.order.get_orderline(child_line_id);
                    if (child_line) {
                        child_line.set_quantity(quantity);
                    }
                });
            }
        }

        merge(orderline) {
            if (this.pack_line_id) {
                // This would avoid to call set_quantity twice
                return;
            }
            return super.merge(...arguments);
        }

        set_quantity(quantity, keep_price) {
            super.set_quantity(...arguments);
            if (!this.pack_child_line_ids) {
                this.pack_child_line_ids = [];
            }
            this.set_pack_lines_quantity(quantity);
        }

        get_full_product_name() {
            const name = super.get_full_product_name(...arguments);
            if (this.pack_line_id) {
                return "> " + name;
            }
            return name;
        }

        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.pack_child_line_ids = [];
            
            if (json.pack_parent_line_id) {
                this.pack_parent_line_id = this.order.get_orderline(
                    json.pack_parent_line_id
                );
            }
            if (json.pack_line_id) {
                this.pack_line_id = this.pos.product_pack_line_by_id[json.pack_line_id];
            }
            if (json.pack_child_line_ids && json.pack_child_line_ids.length !== 0) {
                this.pack_child_line_ids = json.pack_child_line_ids;
            }
        }

        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            if (!this.pack_child_line_ids) {
                this.pack_child_line_ids = [];
            }
            
            json.pack_child_line_ids = this.pack_child_line_ids;
            if (this.pack_parent_line_id) {
                json.pack_parent_line_id = this.pack_parent_line_id.id;
            }
            if (this.pack_line_id) {
                json.pack_line_id = this.pack_line_id.id;
            }
            return json;
        }
    };

    Registries.Model.extend(Orderline, PosProductPackOrderline);

    const PosProductPackOrder = (Order) => class PosProductPackOrder extends Order {
        add_product_pack(line) {
            if (!line.pack_child_line_ids) {
                line.pack_child_line_ids = [];
            }
            
            const pack_lines = line.get_pack_lines();
            pack_lines.forEach(pack_line => {
                const product = this.pos.db.get_product_by_id(pack_line.product_id[0]);
                if (product) {
                    const to_merge_line = line.get_pack_line_can_be_merged_with(
                        pack_line
                    );
                    if (to_merge_line) {
                        const new_line = new this.pos.Orderline({}, {
                            pos: this.pos,
                            order: this,
                            product: product
                        });
                        to_merge_line.merge(new_line);
                    } else {
                        const new_line = this.add_product(product, {
                            merge: false,
                        });
                        
                        if (new_line) {
                            new_line.pack_parent_line_id = line;
                            new_line.pack_line_id = pack_line;
                            
                            if (!new_line.pack_child_line_ids) {
                                new_line.pack_child_line_ids = [];
                            }
                            
                            if (!line.pack_child_line_ids) {
                                line.pack_child_line_ids = [];
                            }
                            
                            line.pack_child_line_ids.push(new_line.id);
                            this.save_to_db();
                        }
                    }
                }
            });
        }

        add_product(product, options={}) {
            if (options.merge === undefined) {
                options.merge = true;
            }
            
            const line = super.add_product(product, options);
            
            if (product.pack_ok && line) {
                if (!line.pack_child_line_ids) {
                    line.pack_child_line_ids = [];
                }
                
                this.add_product_pack(line);
            }
            
            return line;
        }

        remove_orderline(line) {
            if (line) {
                if (!line.pack_child_line_ids) {
                    line.pack_child_line_ids = [];
                }
                
                line.remove_pack_line();
            }
            super.remove_orderline(...arguments);
        }

        add_orderline(line) {
            if (line && !line.pack_child_line_ids) {
                line.pack_child_line_ids = [];
            }
            
            super.add_orderline(...arguments);
            
            if (line && line.order == this) {
                if (line.pack_parent_line_id) {
                    if (!line.pack_parent_line_id.pack_child_line_ids) {
                        line.pack_parent_line_id.pack_child_line_ids = [];
                    }
                    
                    line.pack_parent_line_id.pack_child_line_ids.push(line.id);
                }
            }
        }
    };

    Registries.Model.extend(Order, PosProductPackOrder);
});
