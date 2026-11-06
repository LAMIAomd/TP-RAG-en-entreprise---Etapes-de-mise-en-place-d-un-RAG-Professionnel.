# etape4_partie_a.py : partie A, découvrir les embeddings
from sentence_transformers import SentenceTransformer, util

# Charge le modèle d'embedding. Il comprend le français et d'autres langues.
# ATTENTION : au premier lancement, il est téléchargé (environ 470 Mo), ce qui prend quelques minutes.
modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

phrases = [
    "Comment poser un jour de congé ?",
    "Quelle est la procédure pour demander des vacances ?",
    "Mon ordinateur ne se connecte pas au VPN.",
]

# encode() transforme chaque phrase en un vecteur de nombres
vecteurs = modele.encode(phrases)

# shape = (nombre de phrases, taille d'un vecteur) -> sert à répondre à Q8
print(vecteurs.shape)

# Matrice de similarité (cosinus) : chaque case compare deux phrases.
# 1 = sens identique, proche de 0 = aucun rapport. La diagonale vaut 1 (une phrase comparée à elle-même).
print(util.cos_sim(vecteurs, vecteurs))