# Preuves

Validation réalisée localement le 1er octobre 2026 :

- I3 : 7 tests réussis ;
- I3 : 12 lignes lues, 6 acceptées, 4 rejetées et 2 doublons ;
- I4 : 9 tests réussis.

Les tests couvrent notamment les données invalides, les doublons, la signature HMAC,
l'ancienneté d'une requête, les nouvelles tentatives et la quarantaine.

La CI GitHub relance automatiquement les mêmes tests à chaque `push`.
