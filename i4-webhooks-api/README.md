# I4 - Webhooks et API tierce

Ce module contient un récepteur webhook FastAPI et un partenaire local simulé.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Lancement

Dans un premier terminal :

```bash
uvicorn partner:app --port 8001
```

Dans un deuxième terminal :

```bash
WEBHOOK_SECRET=matrice-local-only uvicorn receiver:app --port 8000
```

Le récepteur propose :

- `GET /health` ;
- `POST /webhooks/planning` ;
- `GET /deliveries/{event_id}`.

Le partenaire propose `POST /tickets`. Pour changer son comportement pendant une démonstration :

```bash
curl -X PUT http://127.0.0.1:8001/mode/flaky
```

Modes disponibles : `ok`, `flaky`, `down`, `slow` et `reject`.

## Tests

```bash
pytest
```

Les tests vérifient la signature, l'ancienneté, les doublons, les retries, le timeout et la quarantaine.
