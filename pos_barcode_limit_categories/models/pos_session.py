# Copyright 2026 Moka Tourisme
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import _, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    def find_product_by_barcode(self, barcode, config_id):
        """Refuse a product that "Restrict Categories" keeps off this POS.

        The POS only loads the products of its allowed categories, and asks
        the server for any barcode it does not know. The native lookup ignores
        the categories, so scanning a product of another shop added it anyway.
        """
        result = super().find_product_by_barcode(barcode, config_id)
        config = self.env["pos.config"].browse(config_id)
        product_ids = [vals["id"] for vals in result.get("product.product", [])]
        if not (
            product_ids and config.limit_categories and config.iface_available_categ_ids
        ):
            return result
        forbidden = self.env["product.product"].search(
            [
                ("id", "in", product_ids),
                ("pos_categ_ids", "not in", config._get_available_categories().ids),
            ],
            limit=1,
        )
        if forbidden:
            raise UserError(
                _(
                    "“%(product)s” cannot be sold in this point of sale.",
                    product=forbidden.with_context(
                        display_default_code=False
                    ).display_name,
                )
            )
        return result
