# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import random
import threading

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools
from odoo.tools import exception_to_unicode
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class EventMailScheduler(models.Model):
    """ Event automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on events since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _inherit = 'event.mail'
    _rec_name = 'event_id'
    _description = 'Event Automated Mailing'
    def execute(self):
        for scheduler in self:
            now = fields.Datetime.now()
            if scheduler.interval_type == 'after_sub':
                new_registrations = scheduler.event_id.registration_ids.filtered_domain(
                    [('state', 'not in', ('cancel', 'draft', 'done')), ('email', '!=', False)]
                ) - scheduler.mail_registration_ids.registration_id
                scheduler._create_missing_mail_registrations(new_registrations)

                # execute scheduler on registrations
                scheduler.mail_registration_ids.execute()
                total_sent = len(scheduler.mail_registration_ids.filtered(lambda reg: reg.mail_sent))
                scheduler.update({
                    'mail_done': total_sent >= (scheduler.event_id.seats_reserved + scheduler.event_id.seats_used),
                    'mail_count_done': total_sent,
                })
            else:
                # before or after event -> one shot email
                if scheduler.mail_done or scheduler.notification_type != 'mail':
                    continue
                # no template -> ill configured, skip and avoid crash
                if not scheduler.template_ref:
                    continue
                # do not send emails if the mailing was scheduled before the event but the event is over
                if scheduler.scheduled_date <= now and (scheduler.interval_type != 'before_event' or scheduler.event_id.date_end > now):
                    scheduler.event_id.mail_attendees(scheduler.template_ref.id)
                    scheduler.update({
                        'mail_done': True,
                        'mail_count_done': scheduler.event_id.seats_reserved + scheduler.event_id.seats_used,
                    })
        return True
