# Pour lancer dans le navigateur: streamlit run rag_altea/app.py

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
