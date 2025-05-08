import os
import streamlit as st
from openai import OpenAI
import re
import base64
import nltk
from nltk.stem import WordNetLemmatizer
from typing import Dict

# Sécurisation de la clé API via les secrets de Streamlit ou les variables d'environnement
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Téléchargement des ressources NLTK au besoin
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
lemmatizer = WordNetLemmatizer()

# Base lexicale enrichie
violence_keywords = {
    "verbale": [
        "connard", "connasse", "salope", "va te faire foutre", "ferme ta gueule",
        "bouffon", "bouffonne", "merdeux", "merdeuse", "ta gueule",
        "débile", "débile mentale", "crétin", "crétine", "imbécile", "imbécile heureuse",
        "enculé", "enculée", "fils de pute", "fille de pute", "pute", "p*te",
        "gros con", "grosse conne", "t'es nulle", "t'es bon à rien", "t'es bonne à rien",
        "tu ne sais rien faire", "tu es incapable", "tu me fatigues", "tu ne sers à rien",
        "t'es qu'une merde", "t'es inutile"
    ],
    "psychologique": [
        "tu vas voir", "je vais te faire payer", "personne ne te croira",
        "fais gaffe à toi", "tu l'as bien cherché", "tu sais ce qui arrive",
        "tu vas le regretter", "tu devrais avoir peur", "on en reparlera ce soir",
        "je t'ai à l'œil", "tu vas comprendre ta douleur",
        "tu es à moi", "je te possède", "tu ne peux pas me quitter",
        "je décide pour toi", "je contrôle ta vie"
    ],
    "physique": [
        "te frapper", "casser la gueule", "te tabasser", "t'éclater",
        "te cogner", "te crever", "te briser les os", "je vais te faire mal",
        "je vais te saigner", "je vais t'exploser", "je vais te défoncer"
    ],
    "sexuelle": [
        "violer", "forcer", "je vais te prendre", "t'écarter les jambes",
        "te baiser", "te sucer contre ton gré", "je vais te faire jouir même si tu veux pas",
        "je vais te forcer", "pénétrer de force", "je vais t'humilier sexuellement"
    ],
    "emojis": [
        "🔪", "💦", "👊", "🔫", "😡", "🍆", "😠", "🖕", "🔥"
    ]
}

def format_gpt_result(result: str) -> str:
    lines = result.split("- ")
    formatted = "\n\n".join(f"- {line.strip()}" for line in lines if line.strip())
    return formatted

def extract_gravity_level(text: str):
    levels = {
        "léger": ("🟢", "#e6f4ea"),
        "modéré": ("🟠", "#fff4e5"),
        "sévère": ("🔴", "#fdecea")
    }
    for level, (icon, color) in levels.items():
        if level in text.lower():
            return icon, color, f"{icon} Gravité : {level.capitalize()}"
    return "⚪", "#f5f5f5", "⚪ Gravité non précisée"

def detect_violence(text: str, keywords: Dict[str, list]) -> Dict[str, list]:
    text = text.lower()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in re.findall(r"\w+|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]+", text)]
    found = {cat: [] for cat in keywords}
    for cat, words in keywords.items():
        for word in words:
            if word in text or any(word == w for w in lemmatized_words):
                found[cat].append(word)
    return {k: v for k, v in found.items() if v}

def gpt_analysis(text: str) -> str:
    prompt = f"""
Tu es Serena, une IA protectrice des victimes. Analyse le message suivant en identifiant :
1. S'il contient de la violence (verbale, psychologique, physique, sexuelle, implicite ou explicite)
2. La nature exacte de cette violence
3. Le degré de gravité (léger, modéré, sévère)
4. Un résumé neutre et non traumatique
5. Une estimation du risque immédiat

Message à analyser : "{text}"

Réponds en français sous cette structure :
- Violence détectée : Oui / Non
- Type(s) de violence : ...
- Nature : ...
- Gravité : ...
- Résumé : ...
- Risque immédiat : ...
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es une IA protectrice des victimes dans un cadre judiciaire."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erreur GPT : {e}"

# Interface utilisateur stylisée
st.set_page_config(page_title="Serena - IA protectrice", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    body { background-color: #f4f0fa; }
    .result-box {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Serena - Détection protectrice de contenu violent")

st.markdown("""
Bienvenue sur le prototype de **Serena**, une intelligence artificielle conçue pour protéger les victimes dans le cadre des procédures judiciaires.
""")

with st.form("formulaire_analyse"):
    user_input = st.text_area("📥 Message ou transcription à analyser :", height=200, placeholder="Ex: 'Tu vas le regretter, je vais te faire payer tout ça.'")
    submitted = st.form_submit_button("Analyser le contenu")

if submitted and user_input:
    result = detect_violence(user_input, violence_keywords)
    st.markdown("---")
    if result:
        st.markdown("### ⚠️ Contenu potentiellement violent détecté")
        for cat, words in result.items():
            st.markdown(f"**{cat.capitalize()}** : {', '.join(words)}")
        st.warning("🚨 Ce message contient des éléments violents explicites ou implicites.")
    else:
        st.success("✅ Aucun contenu violent explicite détecté.")

    st.markdown("---")
    st.markdown("### 🤖 Analyse sémantique protectrice par GPT")
    with st.spinner("Analyse en cours..."):
        gpt_result = gpt_analysis(user_input)
        icon, bgcolor, gravity_display = extract_gravity_level(gpt_result)
        formatted = format_gpt_result(gpt_result)
        st.markdown(f"""
            <div class='result-box' style='background-color:{bgcolor};'>
            🧠 <b>Résultat de l'analyse :</b><br><br>
            <pre>{formatted}</pre>
            <p><b>{gravity_display}</b></p>
            </div>
        """, unsafe_allow_html=True)
        st.download_button("📥 Télécharger l'analyse", formatted, file_name="analyse_serena.txt")
else:
    st.info("Entrez un message ci-dessus pour commencer l'analyse.")

st.markdown("---")
st.markdown("### 🧪 Test manuel GPT")
if st.button("📡 Tester GPT à part"):
    with st.spinner("Appel de test à GPT..."):
        test_text = "Tu vas le regretter, tu verras ce que je vais te faire."
        result = gpt_analysis(test_text)
        icon, bgcolor, gravity_display = extract_gravity_level(result)
        formatted = format_gpt_result(result)
        st.markdown(f"""
            <div class='result-box' style='background-color:{bgcolor};'>
            🧠 <b>Réponse GPT (test) :</b><br><br>
            <pre>{formatted}</pre>
            <p><b>{gravity_display}</b></p>
            </div>
        """, unsafe_allow_html=True)
        st.download_button("📥 Télécharger la réponse GPT", formatted, file_name="test_gpt.txt")

