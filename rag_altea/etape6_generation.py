# etape6_generation.py
from openai import OpenAI

from etape5_recherche import rechercher   # on réutilise la recherche de l'étape 5

# Ollama imite l'interface d'OpenAI sur ton ordinateur (adresse localhost:11434).
# La "clé" est factice : Ollama n'en demande pas, mais la bibliothèque en exige une.
client = OpenAI(base_url="http://localhost:11434/v1",
                api_key="ollama")
MODELE = "llama3.2"
# Phrase que le LLM doit répondre quand les extraits ne contiennent pas la réponse
REPLI = "Je ne trouve pas cette information dans la documentation."


def construire_prompt(question, extraits):
    """Assemble le texte envoyé au LLM : consigne + extraits + question."""
    contexte = ""
    # enumerate(..., start=1) numérote les extraits à partir de 1
    for i, e in enumerate(extraits, start=1):
        # TODO fait : "[i] (source, page)" puis le texte, puis une ligne vide
        contexte += f"[{i}] ({e['source']}, page {e['page']})\n{e['texte']}\n\n"

    # Le prompt a 3 parties : la consigne, les extraits, la question
    return f"""Tu es l'assistant interne d'Altéa Services.
Réponds à la question en utilisant UNIQUEMENT les extraits ci-dessous.
Après chaque information, indique le numéro de l'extrait entre crochets, par exemple [1].
Si les extraits ne contiennent pas la réponse, réponds exactement : "{REPLI}"

Extraits :
{contexte}
Question : {question}
Réponse :"""


def repondre(question, k=3):
    """Pipeline complet : recherche des extraits, construction du prompt, appel au LLM."""
    extraits = rechercher(question, k)                 # étape 5
    prompt = construire_prompt(question, extraits)     # on prépare le texte pour le LLM
    reponse = client.chat.completions.create(
        model=MODELE,
        temperature=0,    # 0 = réponses stables et fidèles, sans "créativité"
        messages=[{"role": "user", "content": prompt}],
    )
    # On renvoie le texte de la réponse ET les extraits (pour afficher les sources)
    return reponse.choices[0].message.content, extraits


if __name__ == "__main__":
    # Q4 : afficher le prompt complet pour une question
    question = "Combien de jours de télétravail par semaine ?"
    print("##### Q4 : PROMPT COMPLET #####")
    print(construire_prompt(question, rechercher(question, k=3)))

    # Q5 : 5 questions, dont 2 sans réponse dans la documentation
    print("\n##### Q5 #####")
    questions = [
        "Combien de jours de télétravail par semaine ?",
        "Comment réinitialiser mon mot de passe ?",
        "Quel est le plafond pour un repas du soir en déplacement ?",
        "Quel temps fera-t-il demain ?",                       # sans réponse
        "Quel est le salaire du directeur général ?",          # sans réponse
        "Quel est le prenom de ma mere ?",
    ]
    for q in questions:
        texte, extraits = repondre(q)
        print("\nQUESTION :", q)
        print("REPONSE  :", texte)
        print("EXTRAITS :", [(e["source"], e["page"]) for e in extraits])

    # Q6 : la même question posée directement au LLM, SANS extraits
    print("\n##### Q6 : LLM SEUL (sans RAG) #####")
    q6 = "Combien de jours de télétravail par semaine sont autorisés chez Altéa ?"
    direct = client.chat.completions.create(
        model=MODELE, temperature=0,
        messages=[{"role": "user", "content": q6}],
    )
    print("LLM seul :", direct.choices[0].message.content)
    print("RAG      :", repondre(q6)[0])