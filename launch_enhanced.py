#!/usr/bin/env python3
"""
Script de lancement rapide pour Easy Travel
"""

import os
import sys
import subprocess
from pathlib import Path


def check_requirements():
    """Vérifie que les packages requis sont installés"""
    try:
        import streamlit
        import openai
        import pymongo
        import googlemaps
        import langchain
        import requests
        import pydantic

        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez avec: pip install -r requirements.txt")
        return False


def create_env_if_missing():
    """Crée un fichier .env basique s'il n'existe pas"""
    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        print("📝 Création du fichier .env...")
        env_content = """# Configuration Easy Travel
OPENAI_API_KEY=your_openai_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
OPENWEATHERMAP_API_KEY=your_weather_key_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=easy_travel

# Mode démo (utilise des données mocké si les clés API ne sont pas définies)
DEMO_MODE=true
"""
        env_path.write_text(env_content)
        print(f"✅ Fichier .env créé: {env_path}")
        print("💡 Vous pouvez modifier les clés API dans ce fichier")


def setup_directories():
    """Crée les répertoires nécessaires"""
    directories = ["data", "data/local_data", "data/user_plans", "data/cache", "logs"]

    for dir_name in directories:
        dir_path = Path(__file__).parent / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

    print("✅ Répertoires de données créés")


def create_sample_local_data():
    """Crée des données locales d'exemple si elles n'existent pas"""
    data_dir = Path(__file__).parent / "data" / "local_data"

    if not (data_dir / "paris.json").exists():
        print("🗃️ Création de données locales d'exemple...")

        paris_data = {
            "city_info": {
                "name": "Paris",
                "country": "France",
                "timezone": "Europe/Paris",
                "currency": "EUR",
                "languages": ["Français", "Anglais"],
                "emergency_numbers": {"Police": "17", "SAMU": "15", "Pompiers": "18"},
                "cultural_etiquette": [
                    "Dire 'Bonjour' en entrant dans un magasin",
                    "Tutoiement rare, utilisez 'vous'",
                    "Repas longs, pas de précipitation",
                ],
            },
            "attractions": [
                {
                    "name": "Tour Eiffel",
                    "category": "Monument",
                    "description": "Symbole de Paris, vue panoramique exceptionnelle",
                    "rating": 4.5,
                    "price_level": 3,
                    "duration_visit": 120,
                    "best_time_visit": "Tôt le matin ou en soirée",
                },
                {
                    "name": "Musée du Louvre",
                    "category": "Musée",
                    "description": "Plus grand musée du monde, Joconde et art universel",
                    "rating": 4.7,
                    "price_level": 3,
                    "duration_visit": 180,
                    "best_time_visit": "Matin, réservation conseillée",
                },
            ],
            "restaurants": [
                {
                    "name": "L'As du Fallafel",
                    "cuisine_type": "Moyen-oriental",
                    "description": "Institution du Marais, falafels authentiques",
                    "rating": 4.4,
                    "price_range": "€",
                    "specialties": ["Falafel", "Houmous", "Shawarma"],
                }
            ],
            "transport": [
                {
                    "type": "Métro",
                    "description": "Réseau dense couvrant toute la ville",
                    "cost": "1.90€ le ticket",
                    "tips": [
                        "Pass Navigo pour les séjours longs",
                        "Attention aux pickpockets",
                    ],
                }
            ],
        }

        with open(data_dir / "paris.json", "w", encoding="utf-8") as f:
            import json

            json.dump(paris_data, f, ensure_ascii=False, indent=2)

        print("✅ Données Paris créées")


def launch_app():
    """Lance l'application Streamlit"""
    app_path = Path(__file__).parent / "app_enhanced.py"

    if not app_path.exists():
        print("❌ Fichier app_enhanced.py non trouvé")
        return False

    print("🚀 Lancement de l'application Easy Travel...")
    print("📱 L'interface s'ouvrira dans votre navigateur")
    print("🔄 Pour arrêter l'application: Ctrl+C")

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée")
        return True

    return True


def main():
    """Fonction principale"""
    print("=" * 60)
    print("✈️ EASY TRAVEL - ASSISTANT INTELLIGENT")
    print("=" * 60)

    # Vérifications et préparation
    steps = [
        ("Vérification des dépendances", check_requirements),
        ("Configuration environnement", create_env_if_missing),
        ("Création des répertoires", setup_directories),
        ("Données d'exemple", create_sample_local_data),
    ]

    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Échec: {step_name}")
            return

    print("\n✅ Préparation terminée !")

    # Lancement
    launch_app()


if __name__ == "__main__":
    main()
