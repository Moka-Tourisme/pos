# Copyright 2025 Horvat Damien <damien@moka.cloud>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result["search_params"]["fields"].extend(
            ["pack_ok", "pack_line_ids", "pack_type", "pack_component_price"]
        )
        return result

    def _loader_params_product_template(self):
        result = super()._loader_params_product_template()
        result["search_params"]["fields"].extend(["pack_ok", "pack_type", "pack_component_price"])
        return result

    def _pos_ui_models_to_load(self):
        models_to_load = super()._pos_ui_models_to_load()
        models_to_load.append("product.pack.line")
        return models_to_load

    def _loader_params_product_pack_line(self):
        return {
            "search_params": {
                "domain": [("parent_product_id.available_in_pos", "=", True)],
                "fields": ["parent_product_id", "quantity", "product_id"],
            },
        }

    def _get_pos_ui_product_pack_line(self, params):
        return self.env["product.pack.line"].search_read(
            **params["search_params"]
        )
