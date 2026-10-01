# Rattrapage WEB2 - MATRiCE

Projet individuel de Youva HOUCHE pour les deux modules attribués :

- **I3 - Structuration de flux** ;
- **I4 - Webhooks et API tierce**.

Chaque dossier contient son propre README avec les commandes d'installation, de lancement et de test.

## Prérequis

- Python 3.12 ou une version plus récente ;
- Git.

## Tests rapides

```bash
cd i3-structuration-flux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python pipeline.py data/seances.ndjson --output output
```

Puis, depuis la racine du projet :

```bash
cd i4-webhooks-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Pour lancer I4, ouvrir deux terminaux dans `i4-webhooks-api` :

```bash
source .venv/bin/activate
uvicorn partner:app --port 8001
```

```bash
source .venv/bin/activate
WEBHOOK_SECRET=matrice-local-only uvicorn receiver:app --port 8000
```

## Structure

```text
i3-structuration-flux/  Pipeline de traitement NDJSON
i4-webhooks-api/        Récepteur webhook et partenaire simulé
preuves/                Résultats de validation
JUSTIFICATIONS.md       Choix techniques et limites
SOURCES_IA.md           Déclaration demandée dans le sujet
```
