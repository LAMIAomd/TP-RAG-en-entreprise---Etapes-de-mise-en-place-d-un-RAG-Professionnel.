# app.py
import streamlit as st

from etape6_generation import repondre

st.title("Assistant documentaire Altéa")
question = st.text_input("Votre question")

if question:
    with st.spinner("Recherche dans la documentation…"):
        reponse, extraits = repondre(question)
    st.write(reponse)
    st.subheader("Sources")
    for i, e in enumerate(extraits, start=1):
        # un expander titré "[i] source, page X" qui affiche le texte de l'extrait
        with st.expander(f"[{i}] {e['source']}, page {e['page']}"):
            st.write(e["texte"])


#--------------------------------------------------------------------------------------------
# # app.py
# from pathlib import Path

# import streamlit as st

# from etape6_generation import repondre

# # set_page_config doit être la toute première commande Streamlit
# st.set_page_config(page_title="Assistant Altéa", page_icon="💬")

# # On charge la feuille de style style.css (rangée à côté de app.py) et on l'injecte dans la page
# css = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
# st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# st.title("Assistant documentaire Altéa")
# st.caption("Posez votre question : la réponse vient de la documentation interne, sources à l'appui.")
# question = st.text_input("Votre question", placeholder="Ex. Combien de jours de télétravail par semaine ?")

# if question:
#     with st.spinner("Recherche dans la documentation…"):
#         reponse, extraits = repondre(question)
#     # key="reponse" permet au CSS de cibler ce bloc avec la classe .st-key-reponse
#     with st.container(key="reponse"):
#         st.write(reponse)
#     st.subheader("Sources")
#     for i, e in enumerate(extraits, start=1):
#         # un expander titré "[i] source, page X" qui affiche le texte de l'extrait
#         with st.expander(f"[{i}] {e['source']}, page {e['page']}"):
#             st.write(e["texte"])