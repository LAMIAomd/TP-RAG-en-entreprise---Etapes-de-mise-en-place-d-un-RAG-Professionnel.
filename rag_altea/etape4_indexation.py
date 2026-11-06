# etape4_indexation.py : partie B, ranger les chunks dans la base vectorielle
import chromadb
from sentence_transformers import SentenceTransformer

from etape1_collecte import collecter           # étape 1 : lire les fichiers
from etape2_nettoyage import nettoyer_pages     # étape 2 : nettoyer
from etape3_decoupage import decouper_pages     # étape 3 : découper

TAILLE = 500            # à adapter selon ton choix en Q7
CHEVAUCHEMENT = 50

if __name__ == "__main__":
    # --- Étapes 1 à 3 : on enchaîne collecte, nettoyage, découpage ---
    pages = nettoyer_pages(collecter())
    chunks = decouper_pages(pages, TAILLE, CHEVAUCHEMENT)
    print(len(chunks), "chunks produits")

    # --- Étape 4 : embeddings + indexation ---
    modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # La base est stockée dans le dossier "base_vectorielle" (créé automatiquement)
    client = chromadb.PersistentClient(path="base_vectorielle")
    # get_or_create : récupère la collection "altea" si elle existe, sinon la crée.
    # "cosine" = on mesure la proximité entre vecteurs avec le cosinus.
    collection = client.get_or_create_collection("altea",
                                                 metadata={"hnsw:space": "cosine"})

    textes = [c["texte"] for c in chunks]                              # le texte de chaque chunk
    vecteurs = modele.encode(textes, show_progress_bar=True).tolist()  # un vecteur par chunk

    # upsert = "ajoute ou met à jour" : si l'id existe déjà, le chunk est remplacé, pas dupliqué
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=textes,
        embeddings=vecteurs,
        # TODO fait : pour chaque chunk, ses informations d'origine
        metadatas=[{"source": c["source"], "page": c["page"], "service": c["service"]}
                   for c in chunks],
    )

    # Q10 : le nombre de chunks indexés doit être égal au nombre de chunks produits
    print(collection.count(), "chunks indexés")

    # --- Q11 : première recherche avec 3 questions de salariés ---
    questions = [
        "Combien de jours de télétravail ?",
        "Que faire si je n'arrive pas à me connecter au VPN ?",
        "Quel est le plafond de remboursement d'un repas ?",
    ]
    for question in questions:
        resultat = collection.query(
            query_embeddings=modele.encode([question]).tolist(),  # la question devient un vecteur
            n_results=3,                                          # on demande les 3 chunks les plus proches
        )
        print("\n" + "=" * 70)
        print("QUESTION :", question)
        # resultat["..."] est une liste de listes (une par question posée) : d'où le [0]
        for doc, meta, dist in zip(resultat["documents"][0],
                                   resultat["metadatas"][0],
                                   resultat["distances"][0]):
            print(f"\n- {meta['source']} (page {meta['page']}, service {meta['service']})"
                  f" | distance = {dist:.3f}")
            print("  ", doc[:150].replace("\n", " "), "...")