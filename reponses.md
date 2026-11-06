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
  contexte nécessaire. La recherche renvoie des morceaux incomplets, et il y a beaucoup de chunks.
- **Chunk trop grand** : il mélange plusieurs sujets, donc son vecteur est « dilué » et
  moins précis pour une question donnée. Il consomme aussi plus de place dans le prompt du LLM.
- **Chevauchement** : il répète la fin d'un chunk au début du suivant, pour ne pas perdre
  une information située à la limite entre deux chunks.
- **Taille retenue : 500 caractères avec 50 de chevauchement (69 chunks).** Nos documents font
  entre 800 et 2 000 caractères : 500 garde en général une section entière avec son contexte,
  alors que 200 coupe les phrases et que 1000 mélange plusieurs sujets.

### Étape 4 - Embeddings et indexation

**Q8.** Le modèle `paraphrase-multilingual-MiniLM-L12-v2` produit des vecteurs de dimension
384 (shape = (3, 384) pour 3 phrases). Avec 69 chunks : 69 x 384 = **26 496 nombres**.

**Q9.** 
Les phrases 1 (« Comment poser un jour de congé ? ») et 2 (« Quelle est la procédure pour
demander des vacances ? ») sont proches (valeur élevée dans la matrice), alors que la phrase 3
(sur le VPN) est éloignée des deux. 
Les phrases 1 et 2 n'ont presque aucun mot en commun, mais
le modèle d'embedding représente le **sens** et non les mots : « congé » et « vacances »,
« poser » et « demander » sont proches dans l'espace des vecteurs.

**Q10.** Chunks produits : 69. Chunks indexés : 69.
Les deux nombres sont égaux.

**Q11.**
Les résultats documentés permettent de confirmer les éléments suivants :
- « Combien de jours de télétravail ? » -> `teletravail.pdf`, page 1, score de similarité : **0,709**.
- « Que faire si je n'arrive pas à me connecter au VPN ? » -> le document attendu concerne le VPN (`vpn.txt` dans le corpus), mais le score et le classement exacts ne figurent pas dans les résultats conservés dans la documentation.
- « Quel est le plafond de remboursement d'un repas ? » -> le document de frais professionnels est pertinent. La documentation indique `restauration.txt`, page 1, avec un score de **0,476** pour la question sur le plafond d'un repas d'affaires. Dans l'évaluation de l'étape 7, le document attendu pour cette question est `notes_de_frais.pdf`.

Pour obtenir les scores exacts des deux dernières recherches, il faut relancer `etape5_recherche.py` avec ces trois questions : ils dépendent des résultats effectivement renvoyés par ChromaDB.

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

**Q1.** La fonction `rechercher(question, k=3, service=None)` transforme la question en vecteur avec le même modèle d'embedding que celui utilisé à l'indexation, puis demande à ChromaDB les trois chunks les plus proches. Pour chaque résultat, elle affiche le fichier source, la page, le service et le score (`1 - distance`).

Les résultats chiffrés conservés dans la documentation sont :
- « Combien de jours de télétravail par semaine ? » -> `teletravail.pdf`, page 1, score **0,709**.
- « Comment réinitialiser mon mot de passe ? » -> `mot_de_passe.txt`, page 1, score **0,678**.
- « Quel est le plafond pour un repas d'affaires ? » -> `restauration.txt`, page 1, score **0,476**.
- « Quel est mon prénom ? » (question hors sujet) -> `livret_accueil.pdf`, page 1, score **0,233**.

Le dernier résultat montre qu'une recherche vectorielle renvoie quand même des passages, même lorsque la documentation ne contient pas la réponse.

**Q2.**
- **k = 1** : on récupère uniquement le passage le plus proche. Le contexte envoyé au LLM est court et généralement plus ciblé, mais on risque de manquer une information utile présente dans un autre chunk.
- **k = 3** : on dispose de davantage de contexte et on augmente les chances de retrouver le bon passage, sans trop alourdir le prompt. C'est la valeur retenue par défaut dans le projet.
- **k = 10** : on augmente encore les chances de retrouver le bon document, mais certains passages peuvent être moins pertinents. Le prompt devient plus long et le LLM peut être perturbé par du bruit.

k = 1
  conges_absences.pdf | page 1 | service RH | score 0.582

k = 3
  conges_absences.pdf | page 1 | service RH | score 0.582
  conges_absences.pdf | page 2 | service RH | score 0.525
  conges_absences.pdf | page 2 | service RH | score 0.475

k = 10
  conges_absences.pdf | page 1 | service RH | score 0.582
  conges_absences.pdf | page 2 | service RH | score 0.525
  conges_absences.pdf | page 2 | service RH | score 0.475
  conges_absences.pdf | page 1 | service RH | score 0.443
  conges_absences.pdf | page 1 | service RH | score 0.390
  teletravail.pdf | page 1 | service RH | score 0.376
  teletravail.pdf | page 1 | service RH | score 0.370
  horaires.txt | page 1 | service General | score 0.351
  conges_absences.pdf | page 2 | service RH | score 0.340
  livret_accueil.pdf | page 2 | service General | score 0.324
  

**Q3.** Avec `service="RH"`, la recherche est limitée aux chunks dont la métadonnée `service` vaut `RH`. Avec `service="IT"`, elle ne cherche que dans les documents du service informatique. Pour une question sur les congés, les résultats RH devraient donc être plus pertinents que les résultats IT.

Ce filtre constitue une première séparation des informations entre services. Cependant, ce n'est pas une véritable sécurité : le filtre est appliqué côté application et un utilisateur pourrait le contourner si les droits ne sont pas contrôlés côté serveur. Il faut authentifier les salariés, vérifier leurs autorisations à chaque requête et empêcher l'accès direct aux documents ou à la base.

### Étape 6 - Génération

**Q4.** Le prompt est construit en trois parties :

1. **Consigne** : l'assistant doit répondre uniquement à partir des extraits et citer chaque information avec le numéro de l'extrait. S'il ne trouve pas la réponse, il doit utiliser la phrase de repli.
2. **Extraits** : les trois chunks récupérés, chacun précédé de son numéro, du nom du fichier et du numéro de page.
3. **Question** : la question posée par le salarié.

Exemple de structure du prompt (le contenu exact des extraits dépend du résultat de la recherche) :

```text
Tu es l'assistant interne d'Altéa Services.
Réponds à la question en utilisant UNIQUEMENT les extraits ci-dessous.
Après chaque information, indique le numéro de l'extrait entre crochets, par exemple [1].
Si les extraits ne contiennent pas la réponse, réponds exactement :
"Je ne trouve pas cette information dans la documentation."

Extraits :
[1] (nom_du_document, page X)
Texte du premier extrait...

[2] (nom_du_document, page X)
Texte du deuxième extrait...

[3] (nom_du_document, page X)
Texte du troisième extrait...

Question : question du salarié
Réponse :
```

**Q5.** Les résultats rapportés dans la documentation sont les suivants. La documentation ne donne pas le texte intégral de chaque réponse ni le détail de toutes les sources pour chaque question ; le tableau distingue donc les résultats confirmés des éléments à revérifier dans le terminal.

| Question | Réponse juste ? | Sources citées ? | Phrase de repli quand il le fallait ? |
|---|---|---|---|
| Combien de jours de télétravail par semaine ? | Oui : jusqu'à 2 jours pour un salarié éligible | Oui, réponse avec sources | Non nécessaire |
| Comment réinitialiser mon mot de passe ? | Oui, le document correspondant est retrouvé | Oui, réponse avec sources | Non nécessaire |
| Quel est le plafond pour un repas du soir en déplacement ? | Réponse signalée comme fausse ou incomplète dans l'évaluation du plafond de repas | Le document attendu a été retrouvé, mais la réponse n'est pas correcte | Non |
| Quel temps fera-t-il demain ? | Pas de réponse dans la documentation ; l'assistant ne doit pas inventer | Les extraits ne peuvent pas constituer une source de réponse | Oui |
| Quel est le salaire du directeur général ? | Pas de réponse dans la documentation ; l'assistant ne doit pas inventer | Les extraits ne peuvent pas constituer une source de réponse | Oui |

Le script contient également une sixième question de test (« Quel est le prénom de ma mère ? »), bien que l'énoncé demande cinq questions. Elle est également hors sujet et doit déclencher la phrase de repli si les extraits ne contiennent pas la réponse.

**Q6.** Sans RAG, le LLM ne reçoit aucun document interne. Pour la question « Combien de jours de télétravail par semaine sont autorisés chez Altéa ? », il indique qu'il ne peut pas connaître la politique interne d'Altéa. Avec le RAG, il reçoit les extraits de `teletravail.pdf` et répond que les salariés éligibles peuvent télétravailler jusqu'à **2 jours par semaine**.

Une **hallucination** est une information inventée ou incorrecte présentée par l'IA comme si elle était vraie. Le RAG limite ce risque en fournissant au LLM des passages issus de la documentation et en lui demandant de s'appuyer uniquement sur ces passages. La phrase de repli permet de signaler l'absence d'information plutôt que d'inventer une réponse. Cette méthode réduit les hallucinations, mais ne les élimine pas totalement.

**Q7.** On fixe `temperature=0` pour rendre les réponses plus stables et moins variables. Pour un assistant documentaire, on privilégie la fidélité aux extraits et la reproductibilité plutôt que la créativité. Cela ne garantit toutefois pas que la réponse sera toujours correcte.

### Étape 7 - Évaluation

**Q8.** Le fichier `evaluation.csv` doit contenir dix questions dont on connaît le document source attendu, avec au minimum les colonnes `question` et `document_attendu`. Il sert de jeu de test : on vérifie ensuite si le document attendu apparaît parmi les résultats de recherche.

La documentation confirme que dix questions ont été utilisées, mais ne reproduit pas leur liste complète ni le contenu du fichier CSV. Il faut donc conserver le `evaluation.csv` réellement utilisé pour garantir que les résultats ci-dessous sont reproductibles, plutôt que de reconstituer une liste qui pourrait ne pas correspondre aux tests exécutés.

**Q9.** Le taux de réussite de la recherche correspond au nombre de questions pour lesquelles le document attendu apparaît parmi les k résultats, divisé par le nombre total de questions, puis multiplié par 100.

Résultats obtenus sur les dix questions :

| Valeur de k | Questions où le bon document est trouvé |
|---|---:|
| k = 1 | 90 % (9/10) |
| k = 3 | 100 % (10/10) |
| k = 5 | 100 % (10/10) |

Avec k = 1, la recherche rate la question sur l'adhésion à la mutuelle : un autre document arrive avant le bon résultat. À partir de k = 3, le document attendu est retrouvé pour les dix questions.

**Q10.** Après lecture manuelle des dix réponses générées :
- **80 %** des réponses sont justes, soit 8 réponses sur 10 ;
- **1 réponse** est partielle ;
- **1 réponse** est fausse ;
- **60 %** des réponses sont correctement sourcées, soit 6 réponses sur 10.

La réponse fausse concerne le plafond d'un repas d'affaires : le document attendu (`notes_de_frais.pdf`) avait bien été retrouvé par la recherche, mais le LLM a répondu qu'il ne trouvait pas l'information. Les résultats montrent que la qualité de la recherche ne garantit donc pas à elle seule la qualité de la réponse générée.

**Q11.** La réponse fausse choisie est celle sur le plafond d'un repas d'affaires. Le bon document (`notes_de_frais.pdf`) figurait bien parmi les résultats de recherche : l'erreur vient donc de la génération et non de la recherche.

Une amélioration possible consiste à rendre la consigne du prompt plus explicite : demander au modèle de vérifier chaque extrait avant d'utiliser la phrase de repli, de rechercher les montants et plafonds dans les extraits et de citer le passage qui justifie le montant. On peut aussi conserver k = 3, puisque la recherche retrouve déjà le bon document à cette valeur.

La documentation identifie cette erreur comme un cas où le petit modèle local est trop prudent. Elle ne fournit toutefois pas de mesure après une modification du prompt : le nouveau résultat doit être testé en relançant la question avec le modèle Ollama. Il ne faut donc pas annoncer un taux d'amélioration sans avoir effectué ce test.

### Étape 8 - Mise à disposition et GitHub

**Q12.** Le fichier `app.py` utilise Streamlit pour créer une interface web. Le salarié saisit sa question dans le champ « Votre question ». L'application affiche un indicateur de chargement pendant le traitement, puis la réponse et une rubrique « Sources ». Chaque source est présentée dans un bloc dépliable indiquant le numéro de l'extrait, le nom du fichier et la page ; le texte du passage peut être consulté.

Pour lancer l'application, depuis le dossier `mon_tp`, avec Ollama actif :

```bash
streamlit run rag_altea/app.py
```

La page est ensuite accessible dans le navigateur à l'adresse `http://localhost:8501`. Une capture d'écran de l'application montrant une réponse et ses sources doit être ajoutée au rendu du TP.

**Q14.** Avant de proposer l'assistant à tous les salariés, plusieurs points doivent être traités :

1. **Gestion des droits d'accès** : chaque salarié ne doit accéder qu'aux documents autorisés pour son service ou son rôle. Il faut mettre en place une authentification et des contrôles d'autorisation côté serveur ; un simple filtre de recherche ne suffit pas.
2. **Protection des données personnelles** : les documents internes peuvent contenir des informations personnelles ou confidentielles. Il faut identifier ces données, limiter leur accès, définir des durées de conservation et respecter les règles de protection des données.
3. **Mise à jour des documents** : lorsqu'un document est modifié ou supprimé, la base vectorielle doit être actualisée. Il faut prévoir un processus régulier de réindexation et supprimer les anciens chunks qui ne correspondent plus aux documents.
4. **Hébergement, sécurité et coût du LLM** : Ollama fonctionne ici localement, mais un déploiement pour plusieurs salariés nécessite une machine adaptée, une gestion des accès, des sauvegardes et une surveillance des performances. Il faut aussi anticiper les coûts matériels, la maintenance et la disponibilité du service.
