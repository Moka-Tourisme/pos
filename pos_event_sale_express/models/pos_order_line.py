# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def _prepare_event_registration_vals(self):
        self.ensure_one()
        vals = {
            "pos_order_line_id": self.id,
            "event_ticket_id": self.event_ticket_id.id,
            "event_id": self.event_id.id,
            "partner_id": self.order_id.partner_id.id,
            "name": self.order_id.partner_id.name,
            "email": self.order_id.partner_id.email,
            "state": "done" if self.order_id.config_id.iface_automatically_confirmed else "draft",
        }
        return vals
