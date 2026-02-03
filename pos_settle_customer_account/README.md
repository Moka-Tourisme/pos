# POS Settle Customer Account - Migration Odoo 18

## Vue d'ensemble
Module migré de Odoo 16 vers Odoo 18 pour la gestion des comptes clients dans le Point de Vente.

## Changements effectués lors de la migration

### 1. Manifest (`__manifest__.py`)
- **Version**: Mise à jour de `16.0.0.0.1` vers `18.0.0.0.1`
- **Dépendances**: Conservées identiques (point_of_sale, account, uom, product, website_sale)
- **Assets**: Structure maintenue pour Odoo 18

### 2. Modèles Python
- **res_partner.py**: Aucune modification nécessaire - compatible Odoo 18
- **pos_order.py**: Ajout de l'import `UserError` manquant depuis `odoo.exceptions`

### 3. Vues XML
- Toutes les vues maintenues telles quelles - compatibles avec Odoo 18
- Templates QWeb conformes aux standards Odoo 18
- Pas de changement dans la structure des rapports

### 4. Assets
- Fichier CSS maintenu sans modification
- Structure des assets compatible avec Odoo 18

## Points de vigilance

### APIs compatibles
- `@api.depends` - Compatible ✓
- `fields.Boolean`, `fields.Float` - Compatible ✓
- `_for_xml_id()` - Compatible ✓
- `reconcile()` sur account.move.line - Compatible ✓

### Fonctionnalités testées
- Création de factures groupées par partenaire
- Réconciliation automatique des écritures comptables
- Génération de rapports PDF
- Envoi d'emails avec templates

## Installation

1. Copier le module dans le répertoire addons
2. Mettre à jour la liste des modules
3. Installer le module `pos_settle_customer_account`

## Dépendances
- point_of_sale
- account
- uom
- product
- website_sale

## Auteurs
- Copyright 2024 Moka - Horvat Damien
- Copyright 2024 Moka - Duciell Romain

## Licence
AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
