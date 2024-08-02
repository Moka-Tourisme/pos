from odoo import models

class SaleReport(models.Model):
    _inherit = "sale.report"

    def _group_by_pos(self):
        res = super()._group_by_pos()
        return f"""
            {res},
            l.event_id,
            l.event_ticket_id,
            l.event_session_id
        """

    def _select_pos(self, fields=None):
        if not fields:
            fields = {}
        fields['event_id'] = ", l.event_id AS event_id"
        fields['event_ticket_id'] = ", l.event_ticket_id AS event_ticket_id"
        fields['event_session_id'] = ", l.event_session_id AS event_session_id"
        return super()._select_pos(fields)