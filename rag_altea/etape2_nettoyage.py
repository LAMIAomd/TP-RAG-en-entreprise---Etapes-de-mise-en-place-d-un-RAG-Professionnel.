# etape2_nettoyage.py
import re   # re = "expressions régulières" : un outil pour chercher/remplacer des motifs dans du texte

from etape1_collecte import collecter   # on réutilise le code de l'étape 1


def nettoyer(texte):
    """Nettoie le texte d'une page."""
    # 1) plusieurs espaces ou tabulations d'affilée -> un seul espace
    #    r"[ \t]+" = "un ou plusieurs espaces ou tabulations"
    texte = re.sub(r"[ \t]+", " ", texte)

    # 2) TODO fait : 3 sauts de ligne ou plus -> exactement 2 (une seule ligne vide)
    #    r"\n{3,}" = "3 retours à la ligne ou plus"
    texte = re.sub(r"\n{3,}", "\n\n", texte)

    # 3) TODO fait : recoller les mots coupés en fin de ligne
    #    Ex. "télé-\ntravail" devient "télétravail"
    #    r"-\n(\w)" = un tiret, un retour à la ligne, puis une lettre (mise de côté dans le "groupe 1")
    #    r"\1"      = on remet seulement cette lettre : le tiret et le retour à la ligne disparaissent
    texte = re.sub(r"-\n(\w)", r"\1", texte)

    # strip() enlève les espaces et sauts de ligne au début et à la fin du texte
    return texte.strip()


def nettoyer_pages(pages):
    """Q3 : nettoie toutes les pages et supprime celles qui sont devenues vides."""
    propres = []
    for p in pages:
        p["texte"] = nettoyer(p["texte"])
        if p["texte"]:               # une chaîne vide "" vaut False : on garde seulement les pages non vides
            propres.append(p)
    return propres


if __name__ == "__main__":
    pages = collecter()
    print("Pages avant nettoyage :", len(pages))

    # Q4 : on choisit la première page d'un PDF (les .txt n'ont pas d'en-tête répété)
    exemple = next(p for p in pages if p["source"].endswith(".pdf"))
    avant = exemple["texte"]         # texte brut, gardé de côté pour comparer

    pages = nettoyer_pages(pages)
    print("Pages après nettoyage :", len(pages))

    # On retrouve la même page (même fichier, même numéro) après nettoyage
    apres = next(p["texte"] for p in pages
                 if p["source"] == exemple["source"] and p["page"] == exemple["page"])

    # repr() affiche les \n et les espaces cachés, ce qui rend la différence visible
    print("\n===== AVANT :", exemple["source"], "page", exemple["page"], "=====")
    print(repr(avant[:500]))
    print("\n===== APRES =====")
    print(repr(apres[:500]))