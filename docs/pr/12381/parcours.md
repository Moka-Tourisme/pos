Base : `wt-12381-pos` (base neuve, `point_of_sale` seul, démo, en français)
Surfaces : pdv
Dimensions : option cochée ; option décochée hors périmètre

Option décochée : le code rend la main au natif avant tout contrôle, rien ne change.

1. Point de vente « Boulangerie » : « Limiter les catégories » est coché, avec Pains et Pâtisseries (option cochée).
2. Ouvrir la caisse (pdv), démarrer une commande vide.
3. Scanner `6016478556493` (« Poubelle à pédale », catégorie Divers).

Résultat attendu : avant, la poubelle est ajoutée au ticket (47,00 $). Après, la fenêtre « Opération invalide » affiche « « Poubelle à pédale » ne se vend pas sur ce point de vente. » et le ticket reste vide.

Billetterie (permanent, événement, séances) hors périmètre : les cartes de programme ne passent pas par le scan.
