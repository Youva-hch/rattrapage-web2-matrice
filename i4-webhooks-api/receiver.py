import hashlib
import hmac
import json
import logging
import os
import time
from datetime import date, datetime
from typing import Literal

import httpx
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator


SECRET = os.getenv("WEBHOOK_SECRET", "matrice-local-only")
PARTNER_URL = os.getenv("PARTNER_URL", "http://127.0.0.1:8001")
MAX_SIZE = 64 * 1024

app = FastAPI(title="Webhook MATRiCE")
deliveries = {}


class Session(BaseModel):
    id: str = Field(min_length=1)
    date: date
    period: Literal["am", "pm"]
    group: Literal["A", "B", "Promotion"]
    mode: Literal["DG", "CE", "AUTO"]
    title: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    teacherId: Literal["t1", "t2", "t3"] | None
    status: Literal["proposed", "confirmed"]

    @model_validator(mode="after")
    def verifier_regles(self):
        if self.mode == "AUTO":
            if self.teacherId is not None or self.status != "proposed":
                raise ValueError("AUTO exige teacherId null et proposed")
        if self.status == "confirmed" and self.teacherId is None:
            raise ValueError("confirmed exige un formateur")
        return self


class Evenement(BaseModel):
    event_id: str = Field(min_length=1)
    type: Literal["session.updated"]
    occurred_at: datetime
    session: Session

    @model_validator(mode="after")
    def verifier_fuseau(self):
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at doit avoir un fuseau")
        return self


def envoyer_au_partenaire(event_id, evenement):
    """Envoie l'événement avec au maximum trois tentatives."""
    record = deliveries[event_id]
    attentes = [0.2, 0.4]

    for tentative in range(1, 4):
        record["attempts"] = tentative
        try:
            reponse = httpx.post(
                f"{PARTNER_URL}/tickets",
                json=evenement,
                headers={"Idempotency-Key": event_id},
                timeout=2,
            )
            if 200 <= reponse.status_code < 300:
                record["status"] = "delivered"
                logging.info("Livraison réussie event_id=%s", event_id)
                return

            temporaire = reponse.status_code == 429 or reponse.status_code >= 500
            if not temporaire:
                record["status"] = "quarantine"
                return
        except httpx.TimeoutException:
            logging.warning("Timeout partenaire event_id=%s", event_id)

        if tentative < 3:
            time.sleep(attentes[tentative - 1])

    record["status"] = "quarantine"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhooks/planning")
async def recevoir_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_timestamp: str = Header(default="", alias="X-Timestamp"),
    x_signature: str = Header(default="", alias="X-Signature"),
):
    corps = await request.body()
    if len(corps) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="corps supérieur à 64 Ko")

    try:
        timestamp = int(x_timestamp)
    except ValueError:
        raise HTTPException(status_code=401, detail="timestamp invalide")

    if abs(time.time() - timestamp) > 300:
        raise HTTPException(status_code=401, detail="timestamp expiré")

    message = x_timestamp.encode() + b"." + corps
    signature_attendue = "sha256=" + hmac.new(
        SECRET.encode(), message, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature_attendue, x_signature):
        raise HTTPException(status_code=401, detail="signature invalide")

    try:
        donnees = json.loads(corps)
        evenement = Evenement.model_validate(donnees)
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="événement invalide")

    if evenement.event_id in deliveries:
        return {"duplicate": True}

    deliveries[evenement.event_id] = {"status": "pending", "attempts": 0}
    background_tasks.add_task(
        envoyer_au_partenaire,
        evenement.event_id,
        evenement.model_dump(mode="json"),
    )
    return JSONResponse(status_code=202, content={"duplicate": False})


@app.get("/deliveries/{event_id}")
def lire_livraison(event_id):
    if event_id not in deliveries:
        raise HTTPException(status_code=404, detail="livraison inconnue")
    return {"event_id": event_id, **deliveries[event_id]}
