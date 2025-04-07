odoo.define("pos_product_pack.models", function (require) {
    "use strict";

    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const { Order } = require('point_of_sale.models');

    const PosProductPackPosGlobalState = (PosGlobalState) => class PosProductPackPosGlobalState extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            
            this.product_pack_lines = loadedData['product.pack.line'] || [];         
            this.pack_lines_by_product_id = {};
            this.product_pack_lines.forEach(line => {
                const parent_id = line.parent_product_id[0];
                if (!this.pack_lines_by_product_id[parent_id]) {
                    this.pack_lines_by_product_id[parent_id] = [];
                }
                this.pack_lines_by_product_id[parent_id].push(line);
            });
        }
        
        getPackComponents(packProductId) {
            if (!this.pack_lines_by_product_id[packProductId]) {
                return [];
            }
            
            return this.pack_lines_by_product_id[packProductId].map(line => {
                const componentId = line.product_id[0];
                const component = this.db.get_product_by_id(componentId);
                return {
                    product: component,
                    quantity: line.quantity || 1
                };
            }).filter(item => item.product);
        }
    };

    Registries.Model.extend(PosGlobalState, PosProductPackPosGlobalState);

    const PosProductPackOrder = (Order) => class PosProductPackOrder extends Order {
        add_product(product, options={}) {
            
            if (product.pack_ok && product.pack_type === 'detailed' && product.pack_component_price == 'totalized') {
                
                const originalPrice = product.lst_price;
                const newOptions = {...options, price: 0};
                const line = super.add_product(product, newOptions);
                
                if (line) {
                    line.set_unit_price(0);
                }
                
                const packComponents = this.pos.getPackComponents(product.id);
                if (packComponents.length > 0) {
                    
                    const packQty = line ? line.get_quantity() : (options.quantity || 1);
                    
                    packComponents.forEach(component => {
                        if (!component.product) {
                            return;
                        }
                        
                        const componentQty = component.quantity * packQty;
                        
                        super.add_product(component.product, {
                            quantity: componentQty,
                            merge: true
                        });
                    });
                }
                
                return line;
            }
            else if (product.pack_ok && product.pack_type === 'detailed') {
                
                const line = super.add_product(product, options);
                
                const packComponents = this.pos.getPackComponents(product.id);
                if (packComponents.length > 0) {
                    
                    const packQty = line ? line.get_quantity() : (options.quantity || 1);
                    
                    packComponents.forEach(component => {
                        if (!component.product) {
                            return;
                        }
                        
                        const componentQty = component.quantity * packQty;
                        
                        const componentLine = super.add_product(component.product, {
                            quantity: componentQty,
                            merge: true,
                            price: 0
                        });
                        
                        if (componentLine) {
                            componentLine.set_unit_price(0);
                        }
                    });
                }
                
                return line;
            }
            else {
                return super.add_product(product, options);
            }
        }
    };

    Registries.Model.extend(Order, PosProductPackOrder);
});
