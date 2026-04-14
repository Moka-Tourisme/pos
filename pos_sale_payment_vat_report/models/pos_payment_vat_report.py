# Copyright 2025 - Moka Tourisme
# License LGPL-3 - See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosPaymentVatReport(models.Model):
    _name = 'pos.payment.vat.report'
    _description = 'Rapport POS - Ventilation par Mode de Paiement et TVA'
    _auto = False
    _order = 'date desc, payment_method_id, tax_id'

    date = fields.Date(string='Date', readonly=True)
    month = fields.Selection(
        selection=[
            ('1', 'Janvier'),
            ('2', 'Février'),
            ('3', 'Mars'),
            ('4', 'Avril'),
            ('5', 'Mai'),
            ('6', 'Juin'),
            ('7', 'Juillet'),
            ('8', 'Août'),
            ('9', 'Septembre'),
            ('10', 'Octobre'),
            ('11', 'Novembre'),
            ('12', 'Décembre'),
        ],
        string='Mois',
        readonly=True,
    )
    year = fields.Integer(string='Année', readonly=True)
    pos_config_id = fields.Many2one(
        comodel_name='pos.config',
        string='Point de Vente',
        readonly=True,
    )
    payment_method_id = fields.Many2one(
        comodel_name='pos.payment.method',
        string='Mode de Paiement',
        readonly=True,
    )
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Taxe',
        readonly=True,
    )
    tax_rate = fields.Float(string='Taux TVA (%)', readonly=True)
    nb_orders = fields.Integer(string='Nombre de commandes', readonly=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Devise',
        compute='_compute_currency_id',
    )
    amount_total_ttc = fields.Monetary(
        string='CA TTC',
        readonly=True,
        currency_field='currency_id',
    )
    amount_total_ht = fields.Monetary(
        string='CA HT',
        readonly=True,
        currency_field='currency_id',
    )
    amount_tax = fields.Monetary(
        string='TVA collectée',
        readonly=True,
        currency_field='currency_id',
    )

    def action_open_orders(self):
        """Raccourci pour le bouton de la vue liste (une seule ligne)."""
        self.ensure_one()
        return self.action_open_orders_multi()

    def action_open_orders_multi(self):
        """Ouvre les commandes POS pour une ou plusieurs lignes du rapport.
        Appelé depuis le bouton liste (1 ligne) et depuis le patch pivot (N lignes).
        """
        if not self:
            return {}

        # Construction dynamique : une clause par ligne, reliées par OR
        conditions = []
        params = []
        for rec in self:
            conditions.append(
                "(DATE(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Paris') = %s"
                " AND p.payment_method_id = %s"
                " AND rel.account_tax_id = %s"
                " AND ps.config_id = %s)"
            )
            params.extend([rec.date, rec.payment_method_id.id, rec.tax_id.id, rec.pos_config_id.id])

        self.env.cr.execute("""
            SELECT DISTINCT po.id
            FROM pos_order po
            JOIN pos_session ps ON ps.id = po.session_id
            JOIN pos_order_line pol ON pol.order_id = po.id
            JOIN account_tax_pos_order_line_rel rel ON rel.pos_order_line_id = pol.id
            JOIN pos_payment p ON p.pos_order_id = po.id
            WHERE po.state IN ('paid', 'done', 'invoiced')
              AND po.amount_total > 0
              AND ({})
        """.format(" OR ".join(conditions)), params)
        order_ids = [row[0] for row in self.env.cr.fetchall()]

        if len(self) == 1:
            title = "Commandes — %s / %s / %s" % (
                self.payment_method_id.name, self.tax_id.name, self.date)
        else:
            title = "Commandes POS (%d lignes)" % len(self)

        return {
            'type': 'ir.actions.act_window',
            'name': title,
            'res_model': 'pos.order',
            'view_mode': 'tree,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('id', 'in', order_ids)],
            'target': 'current',
        }

    @api.depends_context('company')
    def _compute_currency_id(self):
        """Retourne la devise de la société courante."""
        currency = self.env.company.currency_id
        for record in self:
            record.currency_id = currency

    def init(self):
        """Création ou remplacement de la vue SQL de ventilation proportionnelle."""
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW pos_payment_vat_report AS (
                SELECT
                    ROW_NUMBER() OVER (
                        ORDER BY
                            DATE(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Paris'),
                            pm.id,
                            t.id
                    ) AS id,
                    DATE(
                        po.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE 'Europe/Paris'
                    ) AS date,
                    EXTRACT(
                        MONTH FROM po.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE 'Europe/Paris'
                    )::text AS month,
                    EXTRACT(
                        YEAR FROM po.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE 'Europe/Paris'
                    )::integer AS year,
                    ps.config_id AS pos_config_id,
                    pm.id AS payment_method_id,
                    t.id AS tax_id,
                    t.amount AS tax_rate,
                    COUNT(DISTINCT po.id) AS nb_orders,
                    ROUND(
                        SUM(
                            pol.price_subtotal_incl
                            * p.amount
                            / NULLIF(po.amount_total, 0)
                        )::numeric,
                        2
                    ) AS amount_total_ttc,
                    ROUND(
                        SUM(
                            pol.price_subtotal
                            * p.amount
                            / NULLIF(po.amount_total, 0)
                        )::numeric,
                        2
                    ) AS amount_total_ht,
                    ROUND(
                        SUM(
                            (pol.price_subtotal_incl - pol.price_subtotal)
                            * p.amount
                            / NULLIF(po.amount_total, 0)
                        )::numeric,
                        2
                    ) AS amount_tax
                FROM pos_order po
                JOIN pos_session ps ON ps.id = po.session_id
                JOIN pos_order_line pol ON pol.order_id = po.id
                JOIN account_tax_pos_order_line_rel rel
                    ON rel.pos_order_line_id = pol.id
                JOIN account_tax t ON t.id = rel.account_tax_id
                JOIN pos_payment p ON p.pos_order_id = po.id
                JOIN pos_payment_method pm ON pm.id = p.payment_method_id
                WHERE po.state IN ('paid', 'done', 'invoiced')
                  AND po.amount_total > 0
                GROUP BY
                    DATE(
                        po.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE 'Europe/Paris'
                    ),
                    EXTRACT(
                        MONTH FROM po.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE 'Europe/Paris'
                    ),
                    EXTRACT(
                        YEAR FROM po.date_order AT TIME ZONE 'UTC'
                        AT TIME ZONE 'Europe/Paris'
                    ),
                    ps.config_id,
                    pm.id,
                    t.id,
                    t.amount
            )
        """)
