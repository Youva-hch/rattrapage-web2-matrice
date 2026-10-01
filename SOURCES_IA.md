# Sources et usages de l’IA

## Outil utilisé

OpenAI Codex a été utilisé ponctuellement comme outil d’accompagnement.

## Usages

L’IA a été utilisée pour :

- clarifier certaines consignes des modules I3 et I4 ;
- relire la structure générale du dépôt ;
- accompagner certains choix techniques ;
- suggérer des cas limites à tester ;
- aider à reformuler certaines parties de la documentation.

## Fichiers concernés

Les échanges ont principalement concerné :

- `i3-structuration-flux/pipeline.py` ;
- `i3-structuration-flux/tests/test_pipeline.py` ;
- `i4-webhooks-api/receiver.py` ;
- `i4-webhooks-api/partner.py` ;
- `i4-webhooks-api/tests/test_webhooks.py` ;
- `README.md` et `JUSTIFICATIONS.md`.

## Exemples de requêtes

Exemples représentatifs des questions posées :

- « Quelles sont les étapes attendues pour le pipeline NDJSON ? »
- « Quels cas limites faut-il tester pour les dates et les doublons ? »
- « Comment expliquer simplement l’idempotence d’un webhook ? »
- « Peux-tu relire le README et signaler les informations manquantes ? »

## Adaptations réalisées

Les suggestions ont été relues et adaptées pour conserver un code simple correspondant au niveau du projet. Les noms, la structure, les messages d’erreur et les explications ont été reformulés lorsque nécessaire.

## Vérifications

Le code et les tests ont été réalisés et vérifiés par l’étudiant. Les vérifications comprennent :

- l’exécution des tests avec `pytest` ;
- le contrôle du résultat du pipeline sur le fichier fourni ;
- la vérification des signatures, doublons, retries et erreurs du webhook ;
- l’exécution automatique des tests avec GitHub Actions.

L’étudiant reste capable d’expliquer le code, les tests et les choix techniques présentés.