import time

from fastapi import FastAPI, Header, HTTPException


app = FastAPI(title="Partenaire MATRiCE simulé")
mode_actuel = "ok"
tentatives = {}
tickets_crees = set()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.put("/mode/{nouveau_mode}")
def changer_mode(nouveau_mode):
    global mode_actuel
    modes = ["ok", "flaky", "down", "slow", "reject"]
    if nouveau_mode not in modes:
        raise HTTPException(status_code=400, detail="mode inconnu")
    mode_actuel = nouveau_mode
    tentatives.clear()
    tickets_crees.clear()
    return {"mode": mode_actuel}


@app.post("/tickets")
def creer_ticket(donnees: dict, idempotency_key: str = Header(alias="Idempotency-Key")):
    del donnees
    tentatives[idempotency_key] = tentatives.get(idempotency_key, 0) + 1

    if idempotency_key in tickets_crees:
        return {"created": False, "duplicate": True}
    if mode_actuel == "slow":
        time.sleep(3)
    if mode_actuel == "reject":
        raise HTTPException(status_code=400, detail="ticket refusé")
    if mode_actuel == "down":
        raise HTTPException(status_code=503, detail="partenaire indisponible")
    if mode_actuel == "flaky" and tentatives[idempotency_key] == 1:
        raise HTTPException(status_code=503, detail="premier essai en échec")

    tickets_crees.add(idempotency_key)
    return {"created": True, "duplicate": False}
