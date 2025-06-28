import streamlit as st
import openai
import googlemaps
import os
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

# Fonction OpenAI
def ask_chatbot(city, theme):
    prompt = f"""
Tu es un expert en tourisme. Donne-moi 3 idées de lieux à visiter à {city} sur le thème "{theme}".
Formate ta réponse sous forme de liste numérotée avec une phrase d’explication par lieu.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Erreur OpenAI : {e}"

# Fonction Google Maps
def verify_city(city_name):
    try:
        result = gmaps.geocode(city_name)
        if result:
            return result[0]['formatted_address']
        return "Ville non trouvée"
    except Exception as e:
        return f"❌ Erreur Google Maps : {e}"

# Interface Streamlit
st.set_page_config(page_title="Easy Travel", page_icon="✈️")
st.title("🌍 Easy Travel - Chatbot de suggestions touristiques")

with st.form("travel_form"):
    city = st.text_input("🏙️ Ville à visiter", "Rome")
    theme = st.selectbox("🎯 Thème", ["culture", "gastronomie", "nature", "histoire", "architecture"])
    submitted = st.form_submit_button("Rechercher")

if submitted:
    st.info(f"📍 Vérification de la ville : `{city}`")
    validated_city = verify_city(city)

    if "❌" in validated_city or "non trouvée" in validated_city:
        st.error(validated_city)
    else:
        st.success(f"Ville détectée : {validated_city}")
        st.markdown("### ✨ Suggestions personnalisées :")
        response = ask_chatbot(validated_city, theme)
        st.markdown(response)
