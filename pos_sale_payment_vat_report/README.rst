=====================================
POS - Rapport Ventes par Mode de Paiement et TVA
=====================================

.. |badge1| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

|badge1|

Ce module ajoute un rapport analytique au module Point of Sale permettant de
croiser les **modes de paiement** et les **taux de TVA collectée**, avec une
ventilation proportionnelle du chiffre d'affaires.

**Table of contents**

.. contents::
   :local:

Problème résolu
===============

Une commande POS peut être réglée avec plusieurs modes de paiement (ex : 60 €
en CB + 40 € en espèces). Sans ventilation, il est impossible d'attribuer la
TVA collectée à chaque mode de paiement. Ce module calcule la quote-part de
chaque mode en proportion de son montant sur le total de la commande.

Fonctionnalités
===============

* **Vue SQL** ``pos.payment.vat.report`` avec ventilation proportionnelle
  calculée directement en base de données
* **Vue pivot** interactive : mode de paiement (colonnes) × taux TVA (lignes),
  mesures CA TTC, TVA et CA HT
* **Vue liste et graphique** avec regroupements flexibles
* **Wizard XLSX** : saisie de période et filtre par POS, export en un clic
* **Rapport XLSX** sur deux feuilles :

  * Feuille "Récapitulatif" : tableau croisé mode de paiement × taux TVA
  * Feuille "Détail" : toutes les lignes avec totaux
* Formatage Excel soigné : en-têtes gras fond jaune, montants en euros

Configuration
=============

Aucune configuration requise. Le module s'installe et le rapport est accessible
immédiatement sous **Point of Vente > Rapports**.

Utilisation
===========

#. Accéder à **Point de Vente > Rapports > Rapport TVA par Mode de Paiement**
   pour la vue analytique interactive.
#. Accéder à **Point de Vente > Rapports > Export XLSX TVA / Mode de Paiement**
   pour générer un fichier Excel avec filtres de période.

Dépendances
===========

* ``point_of_sale`` (Odoo standard)
* ``report_xlsx`` (OCA, module ``reporting-engine``)

Credits
=======

Authors
~~~~~~~

* Moka Tourisme

Maintainers
~~~~~~~~~~~

Moka Tourisme <https://www.mokatourisme.fr>
