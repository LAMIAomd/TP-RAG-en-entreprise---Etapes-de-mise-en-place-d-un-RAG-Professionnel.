# etape5_recherche.py
import chromadb
from sentence_transformers import SentenceTransformer

# Le MÊME modèle que pour l'indexation : question et chunks doivent être transformés
# par le même modèle pour que leurs vecteurs soient comparables.
modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# On rouvre la base créée à l'étape 4 (get_collection : elle doit déjà exister).
# Le chemin "base_vectorielle" est relatif : lance toujours le script depuis mon_tp.
collection = chromadb.PersistentClient(path="base_vectorielle").get_collection("altea")


def rechercher(question, k=3, service=None):
    """Renvoie les k chunks les plus proches de la question.
    Si `service` est donné (ex. "RH"), on ne cherche que dans ce service."""
    vecteur = modele.encode([question]).tolist()               # la question devient un vecteur
    filtre = {"service": service} if service else None         # filtre sur la métadonnée "service"
    res = collection.query(query_embeddings=vecteur,
                           n_results=k, where=filtre)
    resultats = []
    # res["..."] est une liste de listes (une par question) : d'où le [0]
    for texte, meta, distance in zip(res["documents"][0],
                                     res["metadatas"][0],
                                     res["distances"][0]):
        # TODO fait : un dictionnaire par chunk trouvé, avec un score = 1 - distance
        # (distance petite = proche ; score proche de 1 = très proche)
        resultats.append({
            "texte": texte,
            "source": meta["source"],
            "page": meta["page"],
            "service": meta["service"],
            "score": 1 - distance,
        })
    return resultats


def afficher(resultats):
    """Petite fonction d'affichage pour nos tests."""
    for r in resultats:
        print(f"  {r['source']} | page {r['page']} | service {r['service']} | score {r['score']:.3f}")


if __name__ == "__main__":
    # Q1 : 3 questions de salariés
    print("##### Q1 #####")
    for question in ["Combien de jours de télétravail par semaine ?",
                     "Comment réinitialiser mon mot de passe ?",
                     "Quel est mon prenom ?",
                     "Quel est le plafond pour un repas d'affaires ?"]:
        print("\nQUESTION :", question)
        afficher(rechercher(question))

    # Q2 : même question avec k = 1, 3 et 10
    print("\n##### Q2 #####")
    question = "Comment poser un congé ?"
    for k in (1, 3, 10):
        print(f"\nk = {k}")
        afficher(rechercher(question, k=k))

    # Q3 : même question RH, avec un filtre RH puis IT
    print("\n##### Q3 #####")
    question = "Combien de jours de congés par an ?"
    for service in ("RH", "IT"):
        print(f"\nservice = {service}")
        afficher(rechercher(question, k=3, service=service))