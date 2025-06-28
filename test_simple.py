#!/usr/bin/env python3
"""
Test simple du système Easy Travel
"""

import os
import sys
from pathlib import Path


def main():
    print("🚀 Easy Travel - Test Simple")
    print("=" * 40)

    # Vérifications de base
    print("1. Vérification de l'environnement...")

    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("app_enhanced.py"):
        print("❌ Erreur: app_enhanced.py non trouvé")
        print("   Assurez-vous d'être dans le répertoire easy_travel-chatbot")
        return False

    print("✅ Fichiers principaux détectés")

    # Vérifier la configuration .env
    if not os.path.exists(".env"):
        print("❌ Erreur: fichier .env manquant")
        return False

    print("✅ Configuration .env trouvée")

    # Vérifier les dépendances
    print("\n2. Test des imports...")

    # Ajouter le chemin au PYTHONPATH
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        import streamlit as st

        print("✅ Streamlit disponible")
    except ImportError:
        print("❌ Streamlit non installé")
        print("   Installez avec: pip install streamlit")
        return False

    try:
        import openai

        print("✅ OpenAI disponible")
    except ImportError:
        print("❌ OpenAI non installé")
        return False

    try:
        from chatbot.bot import EasyTravelChatbot

        print("✅ Chatbot Easy Travel importé")
    except ImportError as e:
        print(f"❌ Erreur import chatbot: {e}")
        return False

    try:
        from services.local_data_service import LocalDataService

        print("✅ Service données locales importé")
    except ImportError as e:
        print(f"❌ Erreur import données locales: {e}")
        return False

    try:
        from services.weather_service import WeatherService

        print("✅ Service météo importé")
    except ImportError as e:
        print(f"❌ Erreur import météo: {e}")
        return False

    # Test rapide des services
    print("\n3. Test des services...")

    try:
        # Test service données locales
        local_service = LocalDataService()
        paris_info = local_service.get_city_info("paris")
        if paris_info:
            print(f"✅ Données Paris: {paris_info.name}")
        else:
            print("⚠️  Données Paris non trouvées (sera créé au premier lancement)")

        # Test service météo
        weather_service = WeatherService()
        print("✅ Service météo initialisé")

        # Test chatbot
        bot = EasyTravelChatbot()
        print("✅ Chatbot initialisé")

    except Exception as e:
        print(f"❌ Erreur lors du test des services: {e}")
        return False

    print("\n✅ SYSTÈME READY!")
    print("\n🚀 Pour lancer l'application:")
    print("   streamlit run app_enhanced.py")
    print("\n📱 L'interface s'ouvrira dans votre navigateur")
    print("   Vous pourrez utiliser:")
    print("   • Mode parcours guidé")
    print("   • Chat libre avec IA")
    print("   • Données météo en temps réel")
    print("   • Recommandations personnalisées")

    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Test terminé avec succès!")
            sys.exit(0)
        else:
            print("\n❌ Échec du test")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
