# etape3_decoupage.py
from etape1_collecte import collecter
from etape2_nettoyage import nettoyer_pages


def decouper(texte, taille=500, chevauchement=50):
    """Coupe un texte en morceaux de `taille` caractères qui se chevauchent."""
    # assert = vérification : si la condition est fausse, le programme s'arrête avec ce message
    assert chevauchement < taille, "le chevauchement doit être plus petit que la taille"
    morceaux = []
    debut = 0                               # position où commence le morceau courant
    while debut < len(texte):               # tant qu'il reste du texte à découper
        fin = debut + taille                # TODO fait : le morceau s'arrête "taille" caractères après le début
        morceaux.append(texte[debut:fin])   # texte[debut:fin] = extrait entre ces deux positions
        if fin >= len(texte):               # on a atteint la fin du texte : terminé
            break
        debut = fin - chevauchement         # TODO fait : le prochain morceau recule de "chevauchement" caractères
    return morceaux


def decouper_pages(pages, taille=500, chevauchement=50):
    """Découpe chaque page et renvoie une liste de chunks avec leurs informations."""
    chunks = []
    for p in pages:
        # enumerate numérote les morceaux d'une même page : 0, 1, 2...
        for i, morceau in enumerate(decouper(p["texte"], taille, chevauchement)):
            chunks.append({
                "id": f"{p['source']}-p{p['page']}-{i}",   # identifiant unique, ex. "vpn.txt-p1-0"
                "texte": morceau,
                "source": p["source"],
                "page": p["page"],
                "service": p["service"],
            })
    return chunks


if __name__ == "__main__":
    # Q5 : test demandé par l'énoncé
    resultat = decouper("abcdefghij", taille=4, chevauchement=1)
    print("Test Q5 :", resultat)
    assert resultat == ["abcd", "defg", "ghij"], "le découpage est incorrect"
    print("Test OK\n")

    # Q6 : on découpe tout le corpus avec 3 réglages différents
    pages = nettoyer_pages(collecter())
    print(f"{'Taille':>8} {'Chevauch.':>10} {'Nb chunks':>10} {'Long. moyenne':>14}")
    for taille, chev in [(200, 20), (500, 50), (1000, 100)]:
        chunks = decouper_pages(pages, taille, chev)
        moyenne = sum(len(c["texte"]) for c in chunks) / len(chunks)
        print(f"{taille:>8} {chev:>10} {len(chunks):>10} {moyenne:>14.1f}")