# Justifications techniques

Le projet utilise Python, FastAPI, Pydantic et pytest, conformément aux outils étudiés en WEB2.

Les deux modules restent indépendants : chacun peut être installé, lancé et testé séparément.

Les choix détaillés et les limites seront ajoutés avec chaque module.

## I3

Le pipeline utilise seulement la bibliothèque standard de Python. Le traitement ligne par ligne permet de continuer après une erreur et évite de charger tout le fichier en mémoire.

La validation est faite avant la recherche des doublons. Une ligne invalide ne réserve donc pas son identifiant. Les dates sont converties directement en ISO sans dépendre du fuseau horaire de la machine.
