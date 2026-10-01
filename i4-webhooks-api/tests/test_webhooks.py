import hashlib
import hmac
import json
import time
from pathlib import Path
import sys

import httpx
import pytest
from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).parents[1]))
import receiver  # noqa: E402


client = TestClient(receiver.app)


class FausseReponse:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.fixture(autouse=True)
def remettre_a_zero(monkeypatch):
    receiver.deliveries.clear()
    monkeypatch.setattr(receiver.time, "sleep", lambda secondes: None)


def evenement(event_id="evt-1"):
    return {
        "event_id": event_id,
        "type": "session.updated",
        "occurred_at": "2026-10-19T09:00:00+02:00",
        "session": {
            "id": "s01",
            "date": "2026-10-19",
            "period": "am",
            "group": "A",
            "mode": "DG",
            "title": "React composants",
            "domain": "web",
            "teacherId": "t1",
            "status": "confirmed",
        },
    }


def envoyer(objet, timestamp=None, signature_valide=True):
    corps = json.dumps(objet, separators=(",", ":")).encode()
    timestamp = timestamp or int(time.time())
    signature = hmac.new(
        receiver.SECRET.encode(),
        str(timestamp).encode() + b"." + corps,
        hashlib.sha256,
    ).hexdigest()
    if not signature_valide:
        signature = "incorrecte"

    return client.post(
        "/webhooks/planning",
        content=corps,
        headers={
            "X-Timestamp": str(timestamp),
            "X-Signature": f"sha256={signature}",
            "Content-Type": "application/json",
        },
    )


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_signature_valide(monkeypatch):
    monkeypatch.setattr(receiver.httpx, "post", lambda *args, **kwargs: FausseReponse(200))
    reponse = envoyer(evenement())

    assert reponse.status_code == 202
    assert reponse.json() == {"duplicate": False}
    assert client.get("/deliveries/evt-1").json()["status"] == "delivered"


def test_signature_invalide():
    assert envoyer(evenement(), signature_valide=False).status_code == 401


def test_timestamp_trop_ancien():
    ancien = int(time.time()) - 301
    assert envoyer(evenement(), timestamp=ancien).status_code == 401


def test_doublon(monkeypatch):
    appels = []

    def partenaire(*args, **kwargs):
        appels.append(1)
        return FausseReponse(200)

    monkeypatch.setattr(receiver.httpx, "post", partenaire)
    assert envoyer(evenement("evt-double")).status_code == 202
    assert envoyer(evenement("evt-double")).json() == {"duplicate": True}
    assert len(appels) == 1


def test_503_puis_succes(monkeypatch):
    codes = iter([503, 200])
    monkeypatch.setattr(
        receiver.httpx, "post", lambda *args, **kwargs: FausseReponse(next(codes))
    )
    envoyer(evenement("evt-flaky"))
    livraison = client.get("/deliveries/evt-flaky").json()

    assert livraison["status"] == "delivered"
    assert livraison["attempts"] == 2


def test_erreur_persistante(monkeypatch):
    monkeypatch.setattr(receiver.httpx, "post", lambda *args, **kwargs: FausseReponse(503))
    envoyer(evenement("evt-down"))
    livraison = client.get("/deliveries/evt-down").json()

    assert livraison["status"] == "quarantine"
    assert livraison["attempts"] == 3


def test_400_sans_retry(monkeypatch):
    appels = []

    def partenaire(*args, **kwargs):
        appels.append(1)
        return FausseReponse(400)

    monkeypatch.setattr(receiver.httpx, "post", partenaire)
    envoyer(evenement("evt-reject"))

    assert receiver.deliveries["evt-reject"]["status"] == "quarantine"
    assert len(appels) == 1


def test_timeout(monkeypatch):
    def partenaire(*args, **kwargs):
        raise httpx.TimeoutException("trop lent")

    monkeypatch.setattr(receiver.httpx, "post", partenaire)
    envoyer(evenement("evt-timeout"))

    assert receiver.deliveries["evt-timeout"] == {"status": "quarantine", "attempts": 3}
