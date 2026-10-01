# I3 - Structuration de flux

Ce module lit un fichier NDJSON ligne par ligne, valide les séances, normalise les valeurs puis supprime les doublons.

## Installation et tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Exécution

```bash
python pipeline.py data/seances.ndjson --output output
```

Le programme crée `acceptes.ndjson`, `rejets.ndjson` et `stats.json`.

Pour le fichier fourni, le résultat attendu est : 12 lignes lues, 6 acceptées, 4 rejetées et 2 doublons.

## Utilisation de la mémoire

Le fichier est lu ligne par ligne. Il n'est donc pas entièrement chargé en mémoire. Seuls les identifiants déjà acceptés sont conservés dans un ensemble pour détecter les doublons. La mémoire utilisée dépend principalement du nombre d'identifiants uniques.
