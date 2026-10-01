import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).parents[1]))
from pipeline import traiter_fichier  # noqa: E402


def seance(id="s01", **changements):
    objet = {
        "id": id,
        "date": "19/10/2026",
        "period": "matin",
        "group": "A",
        "mode": "DG",
        "title": "React composants",
        "domain": "web",
        "teacherId": "t1",
        "status": "confirme",
    }
    objet.update(changements)
    return objet


def lancer(tmp_path, lignes):
    entree = tmp_path / "entree.ndjson"
    entree.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    sortie = tmp_path / "sortie"
    stats = traiter_fichier(entree, sortie)
    return stats, sortie


def test_ligne_valide_normalisee(tmp_path):
    stats, sortie = lancer(tmp_path, [json.dumps(seance())])
    resultat = json.loads((sortie / "acceptes.ndjson").read_text())

    assert stats == {"lus": 1, "acceptes": 1, "rejets": 0, "doublons": 0}
    assert resultat["date"] == "2026-10-19"
    assert resultat["period"] == "am"
    assert resultat["status"] == "confirmed"


def test_ligne_invalide_ne_bloque_pas_la_suite(tmp_path):
    lignes = [json.dumps(seance("bad", date="2026-02-30")), json.dumps(seance("ok"))]
    stats, sortie = lancer(tmp_path, lignes)

    assert stats["rejets"] == 1
    assert stats["acceptes"] == 1
    assert json.loads((sortie / "acceptes.ndjson").read_text())["id"] == "ok"


def test_formats_de_date_non_autorises(tmp_path):
    lignes = [
        json.dumps(seance("compacte", date="20261019")),
        json.dumps(seance("sans_zero", date="1/2/2026")),
    ]
    stats, _ = lancer(tmp_path, lignes)

    assert stats == {"lus": 2, "acceptes": 0, "rejets": 2, "doublons": 0}


def test_doublon(tmp_path):
    lignes = [json.dumps(seance("meme")), json.dumps(seance("meme", title="Copie"))]
    stats, _ = lancer(tmp_path, lignes)
    assert stats["doublons"] == 1


def test_json_malforme_et_ligne_vide(tmp_path):
    stats, _ = lancer(tmp_path, ['{"id":"cassé"', ""])
    assert stats["rejets"] == 2


def test_jeu_de_donnees_fourni(tmp_path):
    entree = Path(__file__).parents[1] / "data" / "seances.ndjson"
    stats = traiter_fichier(entree, tmp_path / "sortie")
    assert stats == {"lus": 12, "acceptes": 6, "rejets": 4, "doublons": 2}


def test_resultat_deterministe(tmp_path):
    entree = Path(__file__).parents[1] / "data" / "seances.ndjson"
    traiter_fichier(entree, tmp_path / "sortie1")
    traiter_fichier(entree, tmp_path / "sortie2")

    for nom in ["acceptes.ndjson", "rejets.ndjson", "stats.json"]:
        assert (tmp_path / "sortie1" / nom).read_bytes() == (tmp_path / "sortie2" / nom).read_bytes()
