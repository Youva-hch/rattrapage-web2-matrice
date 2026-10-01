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

## Fiabilité des livraisons

Chaque événement utilise son `event_id` comme clé d'idempotence. Le partenaire ne crée donc pas deux tickets pour le même événement.

Le récepteur attend au maximum 2 secondes par appel. Il réessaie après 0,2 seconde puis 0,4 seconde pour un timeout, une réponse 429 ou une erreur 5xx. Une autre erreur 4xx n'est pas retentée. Après l'échec final, la livraison passe en quarantaine.

Les logs indiquent seulement l'identifiant de l'événement et le résultat de la livraison. Le secret et la signature ne sont jamais écrits dans les logs.
