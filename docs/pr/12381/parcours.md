# Parcours de validation : le scan respecte « Limiter les catégories »

Tâche moka.cloud #12381 (Jardins de Brocéliande : un porte-clés de la boutique
vendu sur la caisse d'accueil, limitée à la billetterie).

Surfaces : pdv
Dimensions : option « Limiter les catégories » cochée (scan refusé) et décochée (scan accepté, couvert par le test `test_without_restriction_any_product_is_found`)

## Base

Base neuve `wt-12381-pos` : `point_of_sale` seul, données de démo, en français.
Aucun module de billetterie : ce module ne dépend que de `point_of_sale`, et les
cartes de programme de billetterie ne passent pas par le scan (hors périmètre).

## Étapes

1. Point de vente « Boulangerie » : vérifier que « Limiter les catégories » est
   coché, avec Pains et Pâtisseries.
2. Ouvrir la caisse et démarrer une commande vide.
3. Scanner le code-barres `6016478556493` (« Poubelle à pédale », catégorie
   Divers, que la Boulangerie ne vend pas).

## Résultat attendu

- Avant : la poubelle est ajoutée au ticket (47,00 $).
- Après : une fenêtre « Opération invalide » affiche « « Poubelle à pédale » ne
  se vend pas sur ce point de vente. », et le ticket reste vide.

Le script `parcours.py` rejoue ces étapes :
`python3 parcours.py <port> <base> <capture.png>`.
