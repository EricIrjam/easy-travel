#!/usr/bin/env python3
"""
Vérification rapide du système Easy Travel
"""

import sys
import os

# Ajouter le chemin actuel
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_system():
    """Test rapide des composants principaux"""

    print("🔍 VÉRIFICATION SYSTÈME EASY TRAVEL")
    print("=" * 50)

    # Test 1: Fichiers de base
    print("\n1. Vérification des fichiers...")
    essential_files = [
        "app_enhanced.py",
        "requirements.txt",
        ".env",
        "chatbot/bot.py",
        "services/local_data_service.py",
        "services/weather_service.py",
    ]

    for file in essential_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} MANQUANT")

    # Test 2: Variables d'environnement
    print("\n2. Configuration...")

    try:
        from dotenv import load_dotenv

        load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.startswith("sk-"):
            print("✅ Clé OpenAI configurée")
        else:
            print("⚠️  Clé OpenAI manquante ou invalide")

        weather_key = os.getenv("OPENWEATHER_API_KEY")
        if weather_key:
            print(f"✅ Clé météo configurée: {weather_key[:10]}...")
        else:
            print("⚠️  Clé météo manquante (mode démo)")

    except Exception as e:
        print(f"❌ Erreur configuration: {e}")

    # Test 3: Imports
    print("\n3. Test des modules...")

    modules_to_test = [
        ("streamlit", "Interface web"),
        ("openai", "IA OpenAI"),
        ("langchain", "Framework LangChain"),
        ("chatbot.bot", "Chatbot Easy Travel"),
        ("services.local_data_service", "Données locales"),
        ("services.weather_service", "Service météo"),
    ]

    import_success = 0
    for module, description in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {description}")
            import_success += 1
        except ImportError as e:
            print(f"❌ {description}: {e}")

    # Test 4: Services
    print("\n4. Test des services...")

    try:
        from services.local_data_service import LocalDataService

        local_service = LocalDataService()
        print("✅ Service données locales initialisé")

        # Test données Paris
        paris_info = local_service.get_city_info("paris")
        if paris_info:
            print(f"✅ Données Paris: {paris_info.name}")
        else:
            print("⚠️  Données Paris à créer (normal au premier lancement)")

    except Exception as e:
        print(f"❌ Service données locales: {e}")

    try:
        from services.weather_service import WeatherService

        weather_service = WeatherService()
        print("✅ Service météo initialisé")
    except Exception as e:
        print(f"❌ Service météo: {e}")

    try:
        from chatbot.bot import EasyTravelChatbot

        bot = EasyTravelChatbot()
        print("✅ Chatbot Easy Travel initialisé")
    except Exception as e:
        print(f"❌ Chatbot: {e}")

    # Résumé
    print("\n" + "=" * 50)
    if import_success >= 4:
        print("🎉 SYSTÈME OPÉRATIONNEL!")
        print("\n🚀 Pour lancer l'application:")
        print("   streamlit run app_enhanced.py")
        print("\n📱 L'interface web s'ouvrira automatiquement")
        return True
    else:
        print("⚠️  SYSTÈME PARTIELLEMENT FONCTIONNEL")
        print("   Certaines dépendances manquent")
        print("   Installez avec: pip install -r requirements.txt")
        return False


if __name__ == "__main__":
    test_system()
