# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID
from odoo.tools import float_is_zero


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def _update_mail_schedulers(self):
        # OVERRIDE to handle sessions' mail scheduler
        session_records = self.filtered(lambda r: r.session_id and not r.pos_order_id)
        regular_records = self - session_records
        regular_records = regular_records.filtered(lambda r: not r.pos_order_id)
        res = super(EventRegistration, regular_records)._update_mail_schedulers()
        # Similar to super, only we find the schedulers linked to the session
        open_registrations = session_records.filtered(lambda r: r.state == "open")
        if not open_registrations:
            return res
        onsubscribe_schedulers = (
            self.env["event.mail.session"]
            .sudo()
            .search(
                [
                    ("session_id", "in", open_registrations.session_id.ids),
                    ("interval_type", "=", "after_sub"),
                ]
            )
        )

        if not onsubscribe_schedulers:
            return res

        onsubscribe_schedulers.mail_done = False
        onsubscribe_schedulers.with_user(SUPERUSER_ID).execute()
        return res
