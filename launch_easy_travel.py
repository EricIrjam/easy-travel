#!/usr/bin/env python3
"""
Guide de lancement Easy Travel - Assistant IA enrichi
"""

import subprocess
import sys
import os
from pathlib import Path


def check_and_install():
    """Vérifie les dépendances et installe si nécessaire"""
    print("🔧 Vérification des dépendances...")

    try:
        import streamlit
        import openai
        import pymongo
        import langchain

        print("✅ Toutes les dépendances sont présentes")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("📦 Installation automatique...")

        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            )
            print("✅ Dépendances installées")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erreur d'installation")
            return False


def create_env_if_missing():
    """Crée le fichier .env s'il manque"""
    if not Path(".env").exists():
        print("📝 Création du fichier de configuration...")
        env_content = """# Configuration Easy Travel
OPENAI_API_KEY=your_openai_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
OPENWEATHER_API_KEY=demo_key
MONGODB_URI=mongodb://localhost:27017/
"""
        Path(".env").write_text(env_content)
        print("✅ Fichier .env créé")


def check_data():
    """Vérifie que les données sont initialisées"""
    data_path = Path("data/local_data")
    if not data_path.exists() or not list(data_path.glob("*.json")):
        print("📊 Initialisation des données locales...")
        try:
            subprocess.run(
                [sys.executable, "setup_enhanced.py"], check=True, capture_output=True
            )
            print("✅ Données initialisées")
        except subprocess.CalledProcessError:
            print("⚠️ Données partiellement initialisées")
    else:
        print("✅ Données locales présentes")


def launch_application():
    """Lance l'application Streamlit"""
    print("\n🚀 Lancement d'Easy Travel...")
    print("📱 L'interface va s'ouvrir dans votre navigateur")
    print("🔄 Pour arrêter: Ctrl+C dans ce terminal")
    print("\n" + "=" * 50)

    try:
        # Lance Streamlit
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app_enhanced.py",
                "--server.headless",
                "false",
                "--server.enableCORS",
                "false",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 Easy Travel arrêté")
    except Exception as e:
        print(f"\n❌ Erreur de lancement: {e}")
        print("💡 Essayez: python -m streamlit run app_enhanced.py")


def main():
    """Fonction principale de lancement"""
    print("✈️ " + "=" * 50)
    print("  EASY TRAVEL - ASSISTANT VOYAGE IA")
    print("  " + "=" * 50)

    print("\n🎯 Fonctionnalités:")
    print("   • Chat intelligent avec IA")
    print("   • Données locales enrichies")
    print("   • Météo en temps réel")
    print("   • Parcours interactif guidé")
    print("   • Plans de voyage personnalisés")

    print("\n🔧 Préparation...")

    # Vérifications
    steps = [
        ("Dépendances", check_and_install),
        ("Configuration", create_env_if_missing),
        ("Données", check_data),
    ]

    all_ok = True
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            all_ok = False
            break

    if all_ok:
        print("\n✅ Système prêt !")
        response = input("\n🚀 Lancer Easy Travel maintenant ? (y/n): ")
        if response.lower() in ["y", "yes", "oui", "o"]:
            launch_application()
        else:
            print("\n📱 Pour lancer plus tard:")
            print("   python -m streamlit run app_enhanced.py")
    else:
        print("\n❌ Problème de configuration")
        print("💡 Vérifiez les erreurs ci-dessus")


if __name__ == "__main__":
    main()
