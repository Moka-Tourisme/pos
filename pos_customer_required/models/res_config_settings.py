from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_iface_customer_required = fields.Boolean(
        related="pos_config_id.iface_customer_required", readonly=False
    )
