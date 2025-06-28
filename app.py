# app.py
import os
import openai
import googlemaps
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

# Fonction pour interroger OpenAI avec un thème
def ask_chatbot_for_city_and_theme(city, theme):
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
        return f"Erreur OpenAI : {e}"

# Fonction pour géocoder une ville avec Google Maps
def verify_city_location(city_name):
    try:
        result = gmaps.geocode(city_name)
        if result:
            return result[0]['formatted_address']
        return "Ville non trouvée."
    except Exception as e:
        return f"Erreur Google Maps : {e}"

# Interface CLI simple
def main():
    print("🌍 Bienvenue dans le Chatbot Easy Travel !\n")
    city = input("🏙️ Entrez une ville : ")
    theme = input("🎯 Thème souhaité (culture, gastronomie, nature, etc.) : ")

    location = verify_city_location(city)
    if "Erreur" in location or "non trouvée" in location:
        print(location)
        return

    print(f"\n📌 Lieux proposés à {location} sur le thème '{theme}' :\n")
    suggestions = ask_chatbot_for_city_and_theme(city, theme)
    print(suggestions)

if __name__ == "__main__":
    main()
