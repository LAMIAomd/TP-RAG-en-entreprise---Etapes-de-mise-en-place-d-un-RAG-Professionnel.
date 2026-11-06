# etape1_collecte.py
from pathlib import Path          # Path = manipuler des chemins de fichiers
from collections import Counter   # Counter = compter les pages par document

from pypdf import PdfReader       # pypdf = bibliothèque qui lit les PDF


def lire_pdf(chemin):
    """Lit un PDF et renvoie une liste de dictionnaires : un par page."""
    lecteur = PdfReader(chemin)   # ouvre le PDF
    pages = []                    # liste vide qui va recevoir nos pages
    # enumerate donne à la fois le numéro et la page ; start=1 => on compte à partir de 1
    for numero, page in enumerate(lecteur.pages, start=1):
        # TODO fait : extract_text() est la méthode de pypdf qui renvoie le texte d'une page
        texte = page.extract_text()
        # chemin.name = juste le nom du fichier (ex. "teletravail.pdf"), sans le dossier
        pages.append({"source": chemin.name, "page": numero, "texte": texte})
    return pages


def lire_txt(chemin):
    """Lit un fichier texte et renvoie une liste contenant UNE seule page."""
    # TODO fait : encoding="utf-8" est indispensable pour bien lire les accents (é, è, à...)
    texte = chemin.read_text(encoding="utf-8")
    # Un .txt n'a pas de pages : on le considère comme une seule page, numéro 1
    return [{"source": chemin.name, "page": 1, "texte": texte}]


def collecter(dossier="docs"):
    """Parcourt tout le dossier docs/ et renvoie la liste de toutes les pages."""
    pages = []
    # rglob("*") liste TOUS les fichiers et sous-dossiers ; sorted les range par ordre alphabétique
    for chemin in sorted(Path(dossier).rglob("*")):
        service = chemin.parent.name   # nom du dossier qui contient le fichier : RH, IT ou General

        # TODO fait : selon l'extension, on appelle la bonne fonction
        if chemin.suffix == ".pdf":
            nouvelles_pages = lire_pdf(chemin)
        elif chemin.suffix == ".txt":
            nouvelles_pages = lire_txt(chemin)
        else:
            continue   # dossier ou autre fichier : on passe au suivant

        # On ajoute la clé "service" à chaque page, puis on l'ajoute à la liste générale
        for p in nouvelles_pages:
            p["service"] = service
            pages.append(p)
    return pages


if __name__ == "__main__":
    # Ce bloc ne s'exécute que si on lance ce fichier directement
    pages = collecter()
    print(len(pages), "pages lues")

    # Q1 : nombre de pages lues pour chaque document
    compteur = Counter(p["source"] for p in pages)   # compte combien de fois chaque nom de fichier apparaît
    for nom, nb in compteur.items():
        print(f"{nom} : {nb} page(s)")