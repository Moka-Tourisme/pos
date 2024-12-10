from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    require_customer = fields.Boolean(
        string="Require Customer",
        default=False,
    )