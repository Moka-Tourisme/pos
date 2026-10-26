# Copyright 2026 Moka Tourisme
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@tagged("post_install", "-at_install")
class TestFindProductByBarcode(TestPointOfSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        PosCategory = cls.env["pos.category"]
        cls.ticket_categ = PosCategory.create({"name": "Tickets"})
        cls.child_categ = PosCategory.create(
            {"name": "Groups", "parent_id": cls.ticket_categ.id}
        )
        cls.shop_categ = PosCategory.create({"name": "Shop"})
        Product = cls.env["product.product"]
        cls.ticket = Product.create(
            {
                "name": "Adult ticket",
                "available_in_pos": True,
                "barcode": "9990000000017",
                "pos_categ_ids": [(6, 0, cls.ticket_categ.ids)],
            }
        )
        cls.group_ticket = Product.create(
            {
                "name": "Group ticket",
                "available_in_pos": True,
                "barcode": "9990000000024",
                "pos_categ_ids": [(6, 0, cls.child_categ.ids)],
            }
        )
        cls.keyring = Product.create(
            {
                "name": "Keyring",
                "default_code": "KEY01",
                "available_in_pos": True,
                "barcode": "9990000000031",
                "pos_categ_ids": [(6, 0, cls.shop_categ.ids)],
            }
        )
        cls.combo_ticket = Product.create(
            {
                "name": "Ticket with souvenir",
                "available_in_pos": True,
                "barcode": "9990000000055",
                "pos_categ_ids": [(6, 0, (cls.shop_categ | cls.ticket_categ).ids)],
            }
        )
        cls.uncategorized = Product.create(
            {
                "name": "Ice cream",
                "available_in_pos": True,
                "barcode": "9990000000062",
            }
        )
        cls.env["product.packaging"].create(
            {
                "name": "Box of keyrings",
                "product_id": cls.keyring.id,
                "qty": 10,
                "barcode": "9990000000048",
            }
        )
        cls.pos_config.write(
            {
                "limit_categories": True,
                "iface_available_categ_ids": [(6, 0, cls.ticket_categ.ids)],
            }
        )
        cls.pos_config.open_ui()
        cls.session = cls.pos_config.current_session_id

    def _find(self, barcode):
        return self.session.find_product_by_barcode(barcode, self.pos_config.id)

    def test_product_outside_categories_is_refused(self):
        for product in self.keyring | self.uncategorized:
            # The message is translated: only the product name is checked.
            with self.assertRaisesRegex(UserError, product.name):
                self._find(product.barcode)

    def test_packaging_of_product_outside_categories_is_refused(self):
        with self.assertRaisesRegex(UserError, self.keyring.name):
            self._find("9990000000048")

    def test_product_of_allowed_category_or_child_is_found(self):
        for product in self.ticket | self.group_ticket | self.combo_ticket:
            result = self._find(product.barcode)
            self.assertEqual(
                [vals["id"] for vals in result["product.product"]], product.ids
            )

    def test_without_restriction_any_product_is_found(self):
        self.pos_config.with_context(
            bypass_categories_forbidden_change=True
        ).limit_categories = False
        # Without the restriction every category is available: only a product
        # with no category at all tells whether the option is still read.
        result = self._find(self.uncategorized.barcode)
        self.assertEqual(
            [vals["id"] for vals in result["product.product"]],
            self.uncategorized.ids,
        )
