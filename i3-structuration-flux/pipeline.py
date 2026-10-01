import argparse
import json
from datetime import date
from pathlib import Path


PERIODES = {
    "matin": "am",
    "am": "am",
    "après-midi": "pm",
    "apres-midi": "pm",
    "pm": "pm",
}


def normaliser_date(valeur):
    """Transforme une date autorisée au format YYYY-MM-DD."""
    try:
        if "/" in valeur:
            jour, mois, annee = valeur.split("/")
            return date(int(annee), int(mois), int(jour)).isoformat()
        return date.fromisoformat(valeur).isoformat()
    except (ValueError, TypeError):
        raise ValueError("date invalide")


def valider_et_normaliser(seance):
    """Retourne une séance normalisée ou lève ValueError."""
    champs = [
        "id",
        "date",
        "period",
        "group",
        "mode",
        "title",
        "domain",
        "teacherId",
        "status",
    ]
    for champ in champs:
        if champ not in seance:
            raise ValueError(f"champ manquant : {champ}")

    for champ in ["id", "date", "period", "group", "mode", "title", "domain", "status"]:
        if not isinstance(seance[champ], str) or not seance[champ].strip():
            raise ValueError(f"valeur invalide : {champ}")

    resultat = seance.copy()
    resultat["date"] = normaliser_date(seance["date"])

    periode = seance["period"].lower()
    if periode not in PERIODES:
        raise ValueError("période invalide")
    resultat["period"] = PERIODES[periode]

    if seance["group"] not in ["A", "B", "Promotion"]:
        raise ValueError("groupe invalide")
    if seance["mode"] not in ["DG", "CE", "AUTO"]:
        raise ValueError("mode invalide")
    if seance["teacherId"] not in [None, "t1", "t2", "t3"]:
        raise ValueError("formateur invalide")

    statuts = {"propose": "proposed", "confirme": "confirmed"}
    resultat["status"] = statuts.get(seance["status"], seance["status"])
    if resultat["status"] not in ["proposed", "confirmed"]:
        raise ValueError("statut invalide")

    if resultat["mode"] == "AUTO":
        if resultat["teacherId"] is not None or resultat["status"] != "proposed":
            raise ValueError("AUTO exige teacherId null et proposed")
    if resultat["status"] == "confirmed" and resultat["teacherId"] is None:
        raise ValueError("confirmed exige un formateur")

    return resultat


def ecrire_ligne(fichier, objet):
    fichier.write(json.dumps(objet, ensure_ascii=False) + "\n")


def traiter_fichier(entree, dossier_sortie):
    """Traite le fichier ligne par ligne et renvoie les statistiques."""
    entree = Path(entree)
    dossier_sortie = Path(dossier_sortie)
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    stats = {"lus": 0, "acceptes": 0, "rejets": 0, "doublons": 0}
    ids_deja_vus = set()

    with entree.open(encoding="utf-8") as source:
        with (dossier_sortie / "acceptes.ndjson").open("w", encoding="utf-8") as acceptes:
            with (dossier_sortie / "rejets.ndjson").open("w", encoding="utf-8") as rejets:
                for numero, ligne in enumerate(source, start=1):
                    stats["lus"] += 1
                    try:
                        if not ligne.strip():
                            raise ValueError("ligne vide")
                        seance = json.loads(ligne)
                        seance = valider_et_normaliser(seance)
                    except json.JSONDecodeError:
                        stats["rejets"] += 1
                        ecrire_ligne(rejets, {"source_line": numero, "motif": "JSON malformé"})
                        continue
                    except (ValueError, TypeError) as erreur:
                        stats["rejets"] += 1
                        ecrire_ligne(rejets, {"source_line": numero, "motif": str(erreur)})
                        continue

                    if seance["id"] in ids_deja_vus:
                        stats["doublons"] += 1
                        continue

                    ids_deja_vus.add(seance["id"])
                    stats["acceptes"] += 1
                    ecrire_ligne(acceptes, {"source_line": numero, **seance})

    with (dossier_sortie / "stats.json").open("w", encoding="utf-8") as fichier:
        json.dump(stats, fichier, ensure_ascii=False, indent=2)
        fichier.write("\n")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Traitement des séances MATRiCE")
    parser.add_argument("entree", help="fichier NDJSON à traiter")
    parser.add_argument("--output", default="output", help="dossier de sortie")
    args = parser.parse_args()

    stats = traiter_fichier(args.entree, args.output)
    print(
        f"{stats['lus']} lues, {stats['acceptes']} acceptées, "
        f"{stats['rejets']} rejetées, {stats['doublons']} doublons"
    )


if __name__ == "__main__":
    main()
