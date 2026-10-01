# Justifications techniques

Le projet utilise Python, FastAPI, Pydantic et pytest, conformément aux outils étudiés en WEB2.

Les deux modules restent indépendants : chacun peut être installé, lancé et testé séparément.

Les choix détaillés et les limites seront ajoutés avec chaque module.

## I3

Le pipeline utilise seulement la bibliothèque standard de Python. Le traitement ligne par ligne permet de continuer après une erreur et évite de charger tout le fichier en mémoire.

La validation est faite avant la recherche des doublons. Une ligne invalide ne réserve donc pas son identifiant. Les dates sont converties directement en ISO sans dépendre du fuseau horaire de la machine.

## I4

Le récepteur utilise FastAPI et Pydantic pour valider les requêtes. Les livraisons sont conservées dans un dictionnaire Python, car le sujet autorise une mémoire locale.

La signature HMAC est calculée sur le corps brut. Le partenaire reçoit `event_id` dans l'en-tête `Idempotency-Key`. Une erreur temporaire (timeout, 429 ou 5xx) est retentée au maximum trois fois. Une erreur 400 n'est pas retentée.

Cette solution reste volontairement simple. Les données de déduplication sont perdues au redémarrage ; une base de données et une file de tâches seraient nécessaires dans une application de production.
