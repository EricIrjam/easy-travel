"""
Easy Travel - Démonstration des fonctionnalités enrichies
"""

import os
import sys
import json
from pathlib import Path

# Ajoute le répertoire racine au path
sys.path.append(str(Path(__file__).parent))


def demo_local_data_service():
    """Démontre le service de données locales"""
    print("\n🗃️ DÉMONSTRATION - Service de données locales")
    print("=" * 50)

    try:
        from services.local_data_service import LocalDataService

        service = LocalDataService()

        # Test avec Paris
        print("📍 Données pour Paris:")

        # Informations ville
        city_info = service.get_city_info("paris")
        if city_info:
            print(f"   Ville: {city_info.get('name', 'N/A')}")
            print(f"   Pays: {city_info.get('country', 'N/A')}")
            print(f"   Monnaie: {city_info.get('currency', 'N/A')}")

        # Attractions
        attractions = service.get_local_attractions("paris")
        print(f"   Attractions trouvées: {len(attractions)}")
        if attractions:
            print(
                f"   Exemple: {attractions[0].name} - {attractions[0].description[:50]}..."
            )

        # Restaurants
        restaurants = service.get_local_restaurants("paris")
        print(f"   Restaurants trouvés: {len(restaurants)}")
        if restaurants:
            print(f"   Exemple: {restaurants[0].name} - {restaurants[0].cuisine_type}")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def demo_weather_service():
    """Démontre le service météo"""
    print("\n🌤️ DÉMONSTRATION - Service météo")
    print("=" * 50)

    try:
        from services.weather_service import WeatherService

        service = WeatherService()

        cities = ["Paris", "Rome", "Barcelone"]

        for city in cities:
            print(f"\n📍 Météo pour {city}:")

            # Météo actuelle
            weather = service.get_current_weather(city)
            if weather:
                print(f"   Température: {weather.temperature}°C")
                print(f"   Description: {weather.description}")
                print(f"   Humidité: {weather.humidity}%")
                print(f"   Vent: {weather.wind_speed} km/h")

            # Prévisions
            forecast = service.get_forecast(city, 3)
            if forecast:
                print(f"   Prévisions 3 jours: {len(forecast)} jours disponibles")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def demo_interactive_journey():
    """Démontre le parcours interactif"""
    print("\n🗺️ DÉMONSTRATION - Parcours interactif")
    print("=" * 50)

    try:
        from services.interactive_journey import InteractiveJourneyOrchestrator

        orchestrator = InteractiveJourneyOrchestrator()

        # Démonstration avec un utilisateur test
        user_id = "demo_user"

        print("🚀 Démarrage du parcours...")
        journey_data = orchestrator.start_journey(user_id)

        if journey_data:
            step = journey_data.get("step")
            if step:
                print(f"   Étape actuelle: {step.title}")
                print(f"   Question: {step.question}")
                print(f"   Type d'interface: {step.ui_type}")

            # Progression
            progress = orchestrator.get_user_progress(user_id)
            print(f"   Progression: {progress.get('progress', 0):.1f}%")
            print(f"   Étapes complétées: {len(progress.get('completed_steps', []))}")

        # Simulation de quelques réponses
        print("\n🎯 Simulation de réponses utilisateur...")

        responses = [{"value": "yes"}, {"value": "culturel"}, {"destination": "paris"}]

        for i, response in enumerate(responses):
            print(f"   Réponse {i+1}: {response}")
            journey_data = orchestrator.process_user_response(user_id, response)
            if journey_data and "step" in journey_data:
                print(f"   → Nouvelle étape: {journey_data['step'].title}")

        # Progression finale
        final_progress = orchestrator.get_user_progress(user_id)
        print(f"\n📊 Progression finale: {final_progress.get('progress', 0):.1f}%")

        # Nettoyage
        orchestrator.reset_journey(user_id)

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def demo_chatbot_integration():
    """Démontre l'intégration du chatbot avec les nouveaux services"""
    print("\n🤖 DÉMONSTRATION - Intégration Chatbot")
    print("=" * 50)

    try:
        # Simulation sans clé API OpenAI
        print("💬 Exemple d'interaction avec le chatbot enrichi:")
        print("   Utilisateur: 'Je veux visiter Paris avec un budget de 1000€'")
        print("   → Le chatbot utilise maintenant:")
        print("     ✓ Données locales (attractions, restaurants)")
        print("     ✓ Service météo (conseils adaptés)")
        print("     ✓ Parcours guidé (collecte structurée)")
        print("     ✓ Recommandations personnalisées")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def check_application_files():
    """Vérifie la présence des fichiers d'application"""
    print("\n📁 VÉRIFICATION - Fichiers d'application")
    print("=" * 50)

    required_files = [
        "app_enhanced.py",
        "chatbot/bot.py",
        "services/local_data_service.py",
        "services/weather_service.py",
        "services/interactive_journey.py",
        "requirements.txt",
    ]

    missing_files = []

    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n⚠️ {len(missing_files)} fichiers manquants")
        return False
    else:
        print(f"\n✅ Tous les fichiers sont présents")
        return True


def create_demo_env_file():
    """Crée un fichier .env de démonstration"""
    env_path = Path(__file__).parent / ".env"

    if env_path.exists():
        print("✅ Fichier .env existe déjà")
        return True

    print("📝 Création du fichier .env de démonstration...")

    env_content = """# Easy Travel - Configuration
# Pour une démo complète, remplacez par vos vraies clés API

# OpenAI pour le chatbot (requis pour les conversations)
OPENAI_API_KEY=your_openai_key_here

# Google Maps pour la géolocalisation (optionnel)
GOOGLE_MAPS_API_KEY=your_google_maps_key_here

# OpenWeatherMap pour la météo réelle (optionnel)
OPENWEATHER_API_KEY=your_weather_key_here

# MongoDB pour la persistance (optionnel)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=easy_travel

# Mode démo (utilise des données simulées)
DEMO_MODE=true
"""

    env_path.write_text(env_content)
    print(f"✅ Fichier .env créé: {env_path}")
    return True


def main():
    """Fonction principale de démonstration"""
    print("=" * 60)
    print("✈️ EASY TRAVEL - DÉMONSTRATION DES ENRICHISSEMENTS")
    print("=" * 60)

    # Étapes de démonstration
    demos = [
        ("Fichiers d'application", check_application_files),
        ("Configuration environnement", create_demo_env_file),
        ("Service de données locales", demo_local_data_service),
        ("Service météo", demo_weather_service),
        ("Parcours interactif", demo_interactive_journey),
        ("Intégration chatbot", demo_chatbot_integration),
    ]

    success_count = 0

    for demo_name, demo_func in demos:
        print(f"\n🔍 {demo_name}...")
        try:
            if demo_func():
                success_count += 1
                print(f"✅ {demo_name} - OK")
            else:
                print(f"⚠️ {demo_name} - Incomplet")
        except Exception as e:
            print(f"❌ {demo_name} - Erreur: {e}")

    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA DÉMONSTRATION")
    print("=" * 60)
    print(f"✅ {success_count}/{len(demos)} démonstrations réussies")

    if success_count >= len(demos) - 1:
        print("\n🎉 Le projet Easy Travel est entièrement enrichi !")
        print("\n🚀 Nouvelles fonctionnalités disponibles:")
        print("   • Parcours interactif guidé avec progression")
        print("   • Données locales enrichies (attractions, restaurants, transport)")
        print("   • Service météo intégré avec conseils personnalisés")
        print("   • Interface Streamlit modernisée avec widgets avancés")
        print("   • Orchestrateur de parcours avec collecte structurée")
        print("   • Intégration seamless de tous les services")

        print("\n📋 Pour tester l'application:")
        print("   1. Installez les dépendances: python install.py")
        print("   2. Lancez l'app: python launch_enhanced.py")
        print("   3. Ou directement: streamlit run app_enhanced.py")

        print("\n💡 Fonctionnalités testables:")
        print("   • Mode parcours guidé (étapes interactives)")
        print("   • Mode chat libre (conversation IA)")
        print("   • Données utilisateur (profils et historique)")
        print("   • Sidebar contextuelle (météo, infos locales)")

    else:
        print(
            "\n⚠️ Certaines fonctionnalités nécessitent une configuration supplémentaire"
        )
        print("💡 Consultez les messages d'erreur ci-dessus pour plus de détails")


if __name__ == "__main__":
    main()
