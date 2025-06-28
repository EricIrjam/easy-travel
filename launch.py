#!/usr/bin/env python3
"""
Script de lancement et test pour Easy Travel Chatbot
"""

import os
import sys
from dotenv import load_dotenv

# Ajoute le répertoire racine au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def check_environment():
    """Vérifie que l'environnement est correctement configuré"""
    load_dotenv()

    required_vars = ["OPENAI_API_KEY", "MONGODB_URI", "GOOGLE_MAPS_API_KEY"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)

    if missing_vars:
        print("❌ Variables d'environnement manquantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Veuillez configurer ces variables dans le fichier .env")
        return False

    print("✅ Configuration de l'environnement validée")
    return True


def test_database_connection():
    """Test la connexion à MongoDB"""
    try:
        from services.database import UserDatabase

        db = UserDatabase()

        # Test de connexion simple
        db.client.admin.command("ping")
        print("✅ Connexion MongoDB réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        print("💡 Assurez-vous que MongoDB est démarré et accessible")
        return False


def test_openai_connection():
    """Test la connexion à OpenAI"""
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Modèle moins cher pour le test
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Test simple
        response = llm.predict("Dis bonjour en une phrase")
        print("✅ Connexion OpenAI réussie")
        print(f"📋 Test de réponse: {response}")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion OpenAI: {e}")
        return False


def test_chatbot():
    """Test rapide du chatbot"""
    try:
        from chatbot.bot import EasyTravelChatbot

        print("🤖 Initialisation du chatbot...")
        bot = EasyTravelChatbot()

        print("💬 Test de conversation...")
        test_message = "Bonjour, je voudrais planifier un voyage à Paris pour 3 jours avec un budget de 1000 euros"

        response = bot.process_message(test_message, "test_user_123")

        print("✅ Test du chatbot réussi")
        print(f"📋 Réponse du bot: {response[:200]}...")

        # Affiche les préférences extraites
        if bot.user_preferences:
            print("🎯 Préférences extraites:")
            for key, value in bot.user_preferences.items():
                print(f"   - {key}: {value}")

        return True
    except Exception as e:
        print(f"❌ Erreur lors du test du chatbot: {e}")
        import traceback

        traceback.print_exc()
        return False


def launch_streamlit():
    """Lance l'application Streamlit"""
    print("🚀 Lancement de l'application Streamlit...")
    print("📱 L'application sera accessible sur: http://localhost:8501")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")

    os.system("streamlit run app.py")


def main():
    """Fonction principale"""
    print("=" * 60)
    print("🛫 EASY TRAVEL CHATBOT - TESTS ET LANCEMENT")
    print("=" * 60)

    # Vérifications préliminaires
    if not check_environment():
        return

    if not test_database_connection():
        print("⚠️  Continuer sans MongoDB (fonctionnalités limitées)")

    if not test_openai_connection():
        print("❌ Impossible de continuer sans OpenAI")
        return

    if not test_chatbot():
        print("❌ Problème avec le chatbot")
        return

    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
    print("=" * 60)

    # Demande si l'utilisateur veut lancer Streamlit
    response = input("\n🚀 Voulez-vous lancer l'application Streamlit? (y/n): ")
    if response.lower() in ["y", "yes", "oui", "o"]:
        launch_streamlit()
    else:
        print("👋 À bientôt! Vous pouvez lancer l'app avec: streamlit run app.py")


if __name__ == "__main__":
    main()
