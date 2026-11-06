# Réponses du TP RAG - Altéa Services

## Exercice 1

### Étape 1 - Collecte

**Q1.** Résultat du script : 23 pages lues, 15 documents (8 PDF de 2 pages, 7 fichiers
texte de 1 page).

**Q2.** On conserve le nom du fichier, la page et le service pour deux raisons principales :
1. **Citer la source** : l'assistant doit toujours indiquer de quel document vient la
   réponse.
2. **Filtrer la recherche** : grâce au service, on peut limiter la
   recherche aux documents d'un seul service. 
Sans ces métadonnées, on aurait seulement des morceaux de texte anonymes, impossibles à
citer ou à filtrer.

### Étape 2 - Nettoyage

**Q3.** `nettoyer_pages` applique `nettoyer` à toutes les pages et retire celles qui sont
vides. 
Résultat : 23 pages avant, 23 pages après => aucune page vide.

**Q4.** 
Défaut qui reste : chaque page de PDF commence par un en-tête répété (« Altéa Services -
Document interne - Diffusion restreinte ») suivi d'un numéro de page et d'un pied de page
(« Document fictif réalisé à des fins pédagogiques »). Ces phrases n'apportent aucune
information utile, mais elles sont indexées dans chaque chunk et peuvent brouiller la
recherche.
Règle proposée : supprimer avec une expression régulière toute ligne qui commence par
« Altéa Services — Document interne » ou par « Document fictif réalisé », ainsi que la ligne
qui ne contient qu'un numéro de page (par exemple avec re.sub et le drapeau re.MULTILINE).

### Étape 3 - Découpage

**Q5.** `decouper("abcdefghij", taille=4, chevauchement=1)` renvoie `["abcd", "defg", "ghij"]`.
À la main : le pas est taille - chevauchement = 4 - 1 = 3.
- debut = 0 : fin = 4, on prend "abcd". 4 < 10, on continue. debut = 4 - 1 = 3.
- debut = 3 : fin = 7, on prend "defg". 7 < 10, on continue. debut = 7 - 1 = 6.
- debut = 6 : fin = 10, on prend "ghij". fin >= 10 : on s'arrête.
Chaque morceau reprend la dernière lettre du précédent (d, puis g) : c'est le chevauchement.

**Q6.**

| Taille (caractères) | Chevauchement | Nombre de chunks | Longueur moyenne |
|-----|----|----|-------|
| 200 | 20 | 156| 189,3 |
| 500 | 50 | 69 | 422,7 |
| 1000| 100| 38 | 746,4 |

**Q7.**
- **Chunk trop petit** : il contient seulement une phrase ou un bout de phrase, sans le
  contexte nécessaire. La recherche renvoie
 alors des morceaux incomplets, et il y a beaucoup de chunks.
- **Chunk trop grand** : il mélange plusieurs sujets, donc son vecteur est « dilué » et
  moins précis pour une question donnée. Il consomme aussi plus de place dans le prompt du LLM.
- **Chevauchement** : il répète la fin d'un chunk au début du suivant, pour ne pas perdre
  une information située à la limite entre deux chunks.
- **Taille retenue : 500 caractères avec 50 de chevauchement (69 chunks).** Nos documents font
  entre 800 et 2 000 caractères : 500 garde en général une section entière avec son contexte,
  alors que 200 coupe les phrases et que 1000 mélange plusieurs sujets.

### Étape 4 - Embeddings et indexation

**Q8.** Le modèle `paraphrase-multilingual-MiniLM-L12-v2` produit des vecteurs de dimension
**384** (shape = (3, 384) pour 3 phrases). Avec 69 chunks : 69 x 384 = **26 496 nombres**.
(Si ton nombre de chunks est différent : nombre de chunks x 384.)

**Q9.** 
Les phrases 1 (« Comment poser un jour de congé ? ») et 2 (« Quelle est la procédure pour
demander des vacances ? ») sont proches (valeur élevée dans la matrice), alors que la phrase 3
(sur le VPN) est éloignée des deux. Les phrases 1 et 2 n'ont presque aucun mot en commun, mais
le modèle d'embedding représente le **sens** et non les mots : « congé » et « vacances »,
« poser » et « demander » sont proches dans l'espace des vecteurs.

**Q10.** Chunks produits : 69. Chunks indexés : 69.
Les deux nombres sont égaux.

**Q11.** 
- « Combien de jours de télétravail ? » -> ...
- « Que faire si je n'arrive pas à me connecter au VPN ? » -> ...
- « Quel est le plafond de remboursement d'un repas ? » -> ...

**Q12.** Non, le nombre de chunks ne double pas : il reste identique après la deuxième
exécution. `upsert` signifie « ajouter ou mettre à jour » : si un chunk avec le même identifiant
existe déjà, il est remplacé. `add` créerait des doublons ou une erreur. Le jour où un document
est modifié, il faut relancer l'indexation : les chunks gardant le même id sont mis à jour.
(Si le nouveau texte donne moins de chunks, les anciens restent et il faut les supprimer.)

**Q13.** `base_vectorielle/` est exclue de GitHub car c'est un dossier **généré** (il se recrée
à partir des documents), potentiellement volumineux, avec des fichiers binaires qui n'ont pas
leur place dans un dépôt de code. Un collègue qui clone le dépôt installe les dépendances
(`pip install -r requirements.txt`), puis lance `python rag_altea/etape4_indexation.py`, qui
reconstruit la base.

## Exercice 2

### Étape 5 - Recherche

**Q1.** [À COMPLÉTER : coller les résultats (source, page, score) des 3 questions]

**Q2.** Avec k = 1, on obtient un seul chunk : précis, mais on risque de rater l'information
si ce n'est pas le bon. Quand k augmente, on gagne en **rappel** (plus de chances que le bon
passage soit parmi les résultats, utile si la réponse est répartie sur plusieurs chunks).
On perd en **précision** : les derniers résultats ont des scores plus faibles et sont souvent
hors sujet, ce qui ajoute du bruit, allonge le prompt envoyé au LLM (plus lent) et augmente le
risque qu'il mélange des informations. [À COMPLÉTER : citer les scores observés pour k = 10]

**Q3.** [À COMPLÉTER : ce que tu observes] Avec service="RH", on obtient uniquement des chunks RH
pertinents. Avec service="IT", on obtient seulement des chunks IT, avec des scores plus faibles
et sans lien avec la question : le filtre restreint bien le périmètre de recherche.
C'est une première étape vers la confidentialité : on peut réserver à chaque service ses
propres documents. Mais cela ne suffit pas : c'est l'appelant qui choisit le service, sans
authentification ni droits par utilisateur ; il n'y a pas de contrôle de qui pose la question,
et une simple étiquette de métadonnée n'est pas une vraie gestion des accès.