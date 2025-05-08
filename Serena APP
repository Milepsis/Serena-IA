# Serena - Interface de détection de contenu violent (version présentable)

import streamlit as st
from typing import Dict
import re

# Base lexicale enrichie (extrait)
violence_keywords = {
    "verbale": ["connard", "salope", "va te faire foutre", "ferme ta gueule"],
    "psychologique": ["tu vas voir", "je vais te faire payer", "personne ne te croira"],
    "physique": ["te frapper", "casser la gueule", "te tabasser"],
    "sexuelle": ["violer", "forcer", "je vais te prendre"]
}

def detect_violence(text: str, keywords: Dict[str, list]) -> Dict[str, list]:
    text = text.lower()
    found = {cat: [] for cat in keywords}
    for cat, words in keywords.items():
        for word in words:
            if re.search(rf"\b{re.escape(word)}\b", text):
                found[cat].append(word)
    return {k: v for k, v in found.items() if v}

# Interface Streamlit
st.set_page_config(page_title="Serena - IA protectrice", page_icon="🛡️", layout="centered")
st.title("🛡️ Serena - Détection protectrice de contenu violent")

st.markdown("""
Bienvenue sur le prototype de **Serena**, une intelligence artificielle conçue pour protéger les victimes dans le cadre des procédures judiciaires.

💬 Collez un message ou une transcription : l'IA identifiera les éléments violents selon leur nature (verbale, psychologique, physique, sexuelle) et signalera les contenus sensibles pour permettre une analyse judiciaire sans réexposition traumatique.
""")

with st.form("formulaire_analyse"):
    user_input = st.text_area("📝 Message ou transcription à analyser :", height=200, placeholder="Ex: 'Tu vas le regretter, je vais te faire payer tout ça.'")
    submitted = st.form_submit_button("Analyser le contenu")

if submitted and user_input:
    result = detect_violence(user_input, violence_keywords)

    st.divider()
    if result:
        st.markdown("## ⚠️ Contenu potentiellement violent détecté")
        for cat, words in result.items():
            st.markdown(f"**{cat.capitalize()}** : {', '.join(words)}")
        st.warning("Ce message contient des éléments violents. Il est recommandé de le transmettre à l'analyse protectrice complète de Serena (GPT-4).")
    else:
        st.success("✅ Aucun contenu violent détecté dans ce message.")

    st.caption("Cette analyse repose sur une base lexicale. L'étape suivante repose sur une analyse sémantique plus poussée à l'aide de GPT.")
else:
    st.info("Entrez un message ci-dessus pour commencer l'analyse.")
