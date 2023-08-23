# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    iface_event_shop_express = fields.Boolean(
        "Express Event Shop",
        help="speeds up point-of-sale orders for events",
    )

    iface_time_before_event = fields.Integer(
        "Time Before Event",
        help="Number of minutes before the event to use express shop.",
    )

    iface_automatically_confirmed = fields.Boolean(
        "Automatically Confirm Registration",
        help="Automatically confirm event registration when the order is paid.",
    )
