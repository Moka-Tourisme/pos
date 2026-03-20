/** @odoo-module **/

import { PivotController } from "@web/views/pivot/pivot_controller";
import { patch } from "@web/core/utils/patch";

/**
 * Patch du PivotController pour le modèle pos.payment.vat.report :
 * redirige le clic sur une cellule directement vers les commandes POS
 * au lieu d'ouvrir la liste du rapport.
 */
patch(PivotController.prototype, "pos_sale_payment_vat_report.pivot_open_orders", {
    async openView(domain, views, context) {
        if (this.model.metaData.resModel !== "pos.payment.vat.report") {
            return this._super(...arguments);
        }

        // Récupère les IDs des lignes du rapport correspondant au domaine cliqué
        const recordIds = await this.orm.search(
            "pos.payment.vat.report",
            domain,
            { limit: 0 }
        );
        if (!recordIds.length) {
            return;
        }

        // Appelle la méthode Python qui construit le domaine pos.order et retourne l'action
        const action = await this.orm.call(
            "pos.payment.vat.report",
            "action_open_orders_multi",
            [recordIds]
        );
        return this.actionService.doAction(action);
    },
});
