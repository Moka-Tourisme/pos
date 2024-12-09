from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    iface_customer_required = fields.Boolean(
        "Customer Required",
        help="Require a customer to be set on the order.",
        default=False,
    )