from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_res_partner_required_fields_ids = fields.Many2many(
        "ir.model.fields",
        related="pos_config_id.res_partner_required_fields_ids",
        readonly=False,
    )
