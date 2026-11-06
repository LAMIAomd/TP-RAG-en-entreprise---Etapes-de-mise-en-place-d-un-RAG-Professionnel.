# etape7_evaluation.py
import csv
from etape5_recherche import rechercher
from etape6_generation import repondre


def taux_reussite(fichier="evaluation.csv", k=3):
    """Part des questions pour lesquelles le bon document est parmi les k résultats."""
    with open(fichier, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))   # une ligne du CSV = un dictionnaire {colonne: valeur}
    trouves = 0
    for ligne in lignes:
        # noms des documents trouvés par la recherche pour cette question
        sources = [r["source"] for r in rechercher(ligne["question"], k)]
        # TODO fait : le document attendu fait-il partie des sources trouvées ?
        if ligne["document_attendu"] in sources:
            trouves += 1
    return trouves / len(lignes)


def generer_reponses(fichier="evaluation.csv"):
    """Q10 : génère la réponse du RAG pour chaque question, pour les noter à la main."""
    with open(fichier, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    for n, ligne in enumerate(lignes, start=1):
        texte, extraits = repondre(ligne["question"])
        print(f"\n[{n}] QUESTION : {ligne['question']}")
        print(f"    DOCUMENT ATTENDU : {ligne['document_attendu']}")
        print(f"    REPONSE  : {texte}")
        print(f"    EXTRAITS : {[(e['source'], e['page']) for e in extraits]}")


if __name__ == "__main__":
    # Q9 : taux de réussite de la recherche pour k = 1, 3 et 5
    for k in (1, 3, 5):
        print(f"k = {k} : {taux_reussite(k=k):.0%} "
              f"de questions où le bon document est trouvé")

    # Q10 : réponses générées (plusieurs minutes : 10 appels au LLM)
    print("\n##### RÉPONSES GÉNÉRÉES #####")
    generer_reponses()