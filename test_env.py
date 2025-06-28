# test_env.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import openai
import googlemaps

# Chargement des variables d'environnement
load_dotenv()

# 1. Vérif clé OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def test_openai():
    print("🧠 Test OpenAI...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Bonjour"}],
            max_tokens=20
        )
        print("✅ OpenAI OK :", response['choices'][0]['message']['content'].strip())
    except Exception as e:
        print("❌ OpenAI Error :", e)

# 2. Vérif MongoDB
def test_mongo():
    print("🗄️ Test MongoDB...")
    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        dbs = client.list_database_names()
        print("✅ MongoDB OK : bases disponibles :", dbs)
    except Exception as e:
        print("❌ MongoDB Error :", e)

# 3. Vérif Google Maps
def test_googlemaps():
    print("🗺️ Test Google Maps...")
    try:
        gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
        result = gmaps.geocode("Paris, France")
        print("✅ Google Maps OK :", result[0]['formatted_address'])
    except Exception as e:
        print("❌ Google Maps Error :", e)

if __name__ == "__main__":
    print("=" * 40)
    print("🚀 TEST DE L'ENVIRONNEMENT")
    print("=" * 40)
    test_openai()
    test_mongo()
    test_googlemaps()
