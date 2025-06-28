#!/usr/bin/env python3
"""
Script de setup pour Easy Travel - Initialisation des données locales et test des services
"""

import os
import sys
import json
from dotenv import load_dotenv

# Ajoute le répertoire racine au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def setup_environment():
    """Configure l'environnement et crée les répertoires nécessaires"""
    print("🔧 Configuration de l'environnement...")

    # Charge les variables d'environnement
    load_dotenv()

    # Crée les répertoires de données
    data_dirs = ["data", "data/local_data", "data/user_plans", "data/cache", "logs"]

    for dir_path in data_dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"✅ Répertoire créé: {dir_path}")

    print("✅ Configuration de l'environnement terminée")


def initialize_local_data():
    """Initialise les données locales pour les principales destinations"""
    print("📊 Initialisation des données locales...")

    try:
        from services.local_data_service import LocalDataService

        local_service = LocalDataService()
        print("✅ Service de données locales initialisé")

        # Test de récupération des données Paris
        paris_info = local_service.get_city_info("paris")
        if paris_info:
            print(f"✅ Données Paris chargées: {paris_info.name}, {paris_info.country}")

        paris_attractions = local_service.get_local_attractions("paris")
        print(f"✅ {len(paris_attractions)} attractions Paris chargées")

        # Test Rome
        rome_info = local_service.get_city_info("rome")
        if rome_info:
            print(f"✅ Données Rome chargées: {rome_info.name}, {rome_info.country}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation des données locales: {e}")
        return False


def test_weather_service():
    """Test le service météo"""
    print("🌤️ Test du service météo...")

    try:
        from services.weather_service import WeatherService

        weather_service = WeatherService()

        # Test avec des données mock
        weather_paris = weather_service.get_current_weather("paris")
        if weather_paris:
            print(
                f"✅ Météo Paris: {weather_paris.temperature}°C, {weather_paris.description}"
            )

        # Test prévisions
        forecast_paris = weather_service.get_forecast("paris", 3)
        if forecast_paris:
            print(f"✅ Prévisions Paris: {len(forecast_paris)} jours")

        return True

    except Exception as e:
        print(f"❌ Erreur service météo: {e}")
        return False


def test_journey_orchestrator():
    """Test l'orchestrateur de parcours"""
    print("🗺️ Test du parcours interactif...")

    try:
        from services.interactive_journey import InteractiveJourneyOrchestrator

        orchestrator = InteractiveJourneyOrchestrator()

        # Test démarrage de parcours
        test_user_id = "test_user_setup"
        journey_data = orchestrator.start_journey(test_user_id)

        if journey_data and "step" in journey_data:
            step = journey_data["step"]
            print(f"✅ Parcours démarré: {step.title}")

            # Test progression
            progress = orchestrator.get_user_progress(test_user_id)
            print(f"✅ Progression: {progress.get('progress', 0):.0f}%")

        # Nettoyage
        orchestrator.reset_journey(test_user_id)

        return True

    except Exception as e:
        print(f"❌ Erreur orchestrateur de parcours: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_connection():
    """Test la connexion à la base de données"""
    print("🗄️ Test de la base de données...")

    try:
        from services.database import UserDatabase

        db = UserDatabase()

        # Test de connexion
        db.client.admin.command("ping")
        print("✅ Connexion MongoDB réussie")

        # Test création d'un profil utilisateur
        from models.user_profile import UserProfile, UserPreferences

        test_profile = UserProfile(
            user_id="test_setup",
            name="Test User",
            preferences=UserPreferences(
                preferred_destinations=["Paris"], preferred_activities=["culture"]
            ),
        )

        success = db.create_or_update_user_profile(test_profile)
        if success:
            print("✅ Création de profil utilisateur réussie")

        return True

    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        print("💡 Assurez-vous que MongoDB est démarré")
        return False


def create_sample_data():
    """Crée des données d'exemple pour démonstration"""
    print("🎭 Création de données d'exemple...")

    sample_destinations = {
        "barcelone": {
            "city_info": {
                "name": "Barcelone",
                "country": "Espagne",
                "timezone": "Europe/Madrid",
                "currency": "EUR",
                "languages": ["Espagnol", "Catalan", "Anglais"],
                "emergency_numbers": {"Police": "112", "Pompiers": "112"},
                "tipping_culture": "5-10% dans les restaurants",
                "cultural_etiquette": [
                    "Les repas sont tardifs (14h-15h, 21h-22h)",
                    "Sieste de 14h à 17h dans certaines zones",
                    "Saluer avec des bises (2 bises)",
                ],
                "safety_tips": [
                    "Attention aux pickpockets sur Las Ramblas",
                    "Éviter les sacs à dos ouverts dans le métro",
                    "Quartier sûr, mais vigilance la nuit",
                ],
            },
            "attractions": [
                {
                    "name": "Sagrada Família",
                    "category": "Architecture religieuse",
                    "description": "Chef-d'œuvre de Gaudí, basilique unique au monde",
                    "address": "Carrer de Mallorca, 401, 08013 Barcelona",
                    "rating": 4.7,
                    "price_level": 3,
                    "opening_hours": {
                        "lundi": "09:00-18:00",
                        "mardi": "09:00-18:00",
                        "mercredi": "09:00-18:00",
                        "jeudi": "09:00-18:00",
                        "vendredi": "09:00-18:00",
                        "samedi": "09:00-18:00",
                        "dimanche": "10:30-18:00",
                    },
                    "duration_visit": 120,
                    "best_time_visit": "Tôt le matin ou fin d'après-midi",
                    "accessibility": True,
                    "languages_available": ["Espagnol", "Anglais", "Français"],
                    "booking_required": True,
                    "seasonal_info": "Très fréquenté en été, réservation obligatoire",
                },
                {
                    "name": "Park Güell",
                    "category": "Parc artistique",
                    "description": "Parc coloré de Gaudí avec vue panoramique",
                    "address": "08024 Barcelona",
                    "rating": 4.5,
                    "price_level": 2,
                    "opening_hours": {
                        "lundi": "08:00-18:30",
                        "mardi": "08:00-18:30",
                        "mercredi": "08:00-18:30",
                        "jeudi": "08:00-18:30",
                        "vendredi": "08:00-18:30",
                        "samedi": "08:00-18:30",
                        "dimanche": "08:00-18:30",
                    },
                    "duration_visit": 90,
                    "best_time_visit": "Matin pour éviter la foule",
                    "accessibility": False,
                    "languages_available": ["Espagnol", "Anglais"],
                    "booking_required": True,
                    "seasonal_info": "Plus agréable au printemps et automne",
                },
            ],
            "restaurants": [
                {
                    "name": "Cal Pep",
                    "cuisine_type": "Tapas catalanes",
                    "description": "Institution des tapas à Barcelone",
                    "address": "Plaça de les Olles, 8, 08003 Barcelona",
                    "rating": 4.6,
                    "price_range": "€€€",
                    "specialties": ["Tapas de mer", "Jambon ibérique", "Croquettes"],
                    "opening_hours": {
                        "lundi": "Fermé",
                        "mardi": "19:30-01:30",
                        "mercredi": "19:30-01:30",
                        "jeudi": "19:30-01:30",
                        "vendredi": "19:30-01:30",
                        "samedi": "19:30-01:30",
                        "dimanche": "Fermé",
                    },
                    "reservation_required": False,
                    "dietary_options": ["pescetarian"],
                    "atmosphere": "Animé, authentique",
                    "local_favorite": True,
                }
            ],
            "transport": [
                {
                    "type": "Metro",
                    "description": "Réseau moderne et efficace",
                    "cost": "2.40€ le ticket",
                    "duration": "Couvre toute la ville",
                    "frequency": "2-4 minutes",
                    "accessibility": "La plupart des stations",
                    "tips": [
                        "Carte T-10 pour 10 voyages économique",
                        "Évitez les heures de pointe",
                        "Application TMB App très utile",
                    ],
                }
            ],
        }
    }

    # Sauvegarde les données de Barcelone
    data_path = os.path.join(os.path.dirname(__file__), "data", "local_data")
    os.makedirs(data_path, exist_ok=True)

    for city, data in sample_destinations.items():
        file_path = os.path.join(data_path, f"{city}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Données {city.title()} créées")

    return True


def generate_demo_config():
    """Génère un fichier de configuration de démo"""
    print("⚙️ Génération de la configuration de démo...")

    demo_config = {
        "demo_mode": True,
        "mock_apis": {"weather": True, "google_maps": False},
        "default_destinations": ["paris", "rome", "barcelone"],
        "journey_settings": {
            "min_steps": 5,
            "max_duration_minutes": 15,
            "auto_save": True,
        },
        "ui_settings": {
            "theme": "default",
            "animations": True,
            "sidebar_expanded": True,
        },
    }

    config_path = os.path.join(os.path.dirname(__file__), "config", "demo_config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(demo_config, f, ensure_ascii=False, indent=2)

    print(f"✅ Configuration de démo créée: {config_path}")
    return True


def run_full_test():
    """Lance une série de tests complets"""
    print("🧪 Lancement des tests complets...")

    tests = [
        ("Données locales", test_local_data_comprehensive),
        ("Services météo", test_weather_comprehensive),
        ("Parcours utilisateur", test_user_journey_flow),
        ("Intégration complète", test_integration),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
            print(f"   {status}")
        except Exception as e:
            results[test_name] = False
            print(f"   ❌ ERREUR: {e}")

    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 Résultat global: {passed}/{total} tests passés")

    if passed == total:
        print("🎉 Tous les tests sont passés ! Votre système est prêt.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return False


def test_local_data_comprehensive():
    """Test complet des données locales"""
    from services.local_data_service import LocalDataService

    service = LocalDataService()

    # Test toutes les villes
    cities = ["paris", "rome", "barcelone"]

    for city in cities:
        info = service.get_city_info(city)
        if not info:
            return False

        attractions = service.get_local_attractions(city)
        restaurants = service.get_local_restaurants(city)

        if len(attractions) == 0 or len(restaurants) == 0:
            return False

    return True


def test_weather_comprehensive():
    """Test complet du service météo"""
    from services.weather_service import WeatherService

    service = WeatherService()

    cities = ["paris", "rome", "barcelone"]

    for city in cities:
        weather = service.get_current_weather(city)
        if not weather:
            return False

        forecast = service.get_forecast(city, 5)
        if len(forecast) == 0:
            return False

    return True


def test_user_journey_flow():
    """Test du flux complet de parcours utilisateur"""
    from services.interactive_journey import InteractiveJourneyOrchestrator

    orchestrator = InteractiveJourneyOrchestrator()

    # Simule un parcours complet
    user_id = "test_flow_user"

    # Démarrage
    journey_data = orchestrator.start_journey(user_id)
    if not journey_data:
        return False

    # Simulation de quelques étapes
    responses = [
        {"value": "yes"},
        {"value": "culturel"},
        {"value": "has_destination"},
        {"destination": "paris"},
    ]

    for response in responses:
        journey_data = orchestrator.process_user_response(user_id, response)
        if not journey_data:
            return False

    # Vérification progression
    progress = orchestrator.get_user_progress(user_id)
    if progress["progress"] <= 0:
        return False

    # Nettoyage
    orchestrator.reset_journey(user_id)

    return True


def test_integration():
    """Test d'intégration de tous les composants"""
    try:
        # Import de tous les services
        from services.local_data_service import LocalDataService
        from services.weather_service import WeatherService
        from services.interactive_journey import InteractiveJourneyOrchestrator
        from chatbot.bot import EasyTravelChatbot

        # Test création des services
        local_service = LocalDataService()
        weather_service = WeatherService()
        journey_orchestrator = InteractiveJourneyOrchestrator()

        # Test interaction entre services
        user_id = "integration_test"

        # Démarrage parcours
        journey_data = journey_orchestrator.start_journey(user_id)

        # Test données enrichies
        weather = weather_service.get_current_weather("paris")
        local_data = local_service.get_local_attractions("paris")

        if not weather or not local_data:
            return False

        return True

    except Exception as e:
        print(f"Erreur d'intégration: {e}")
        return False


def main():
    """Fonction principale du script de setup"""
    print("=" * 60)
    print("🛫 EASY TRAVEL - SCRIPT DE SETUP AVANCÉ")
    print("=" * 60)

    steps = [
        ("Configuration environnement", setup_environment),
        ("Données locales", initialize_local_data),
        ("Service météo", test_weather_service),
        ("Parcours interactif", test_journey_orchestrator),
        ("Base de données", test_database_connection),
        ("Données d'exemple", create_sample_data),
        ("Configuration démo", generate_demo_config),
    ]

    success_count = 0

    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            result = step_func()
            if result:
                success_count += 1
                print(f"✅ {step_name} terminé avec succès")
            else:
                print(f"⚠️ {step_name} terminé avec des avertissements")
        except Exception as e:
            print(f"❌ Erreur dans {step_name}: {e}")

    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DU SETUP")
    print("=" * 60)
    print(f"✅ {success_count}/{len(steps)} étapes réussies")

    if success_count >= len(steps) - 1:  # Tolère une erreur
        print("\n🎉 Setup terminé avec succès !")
        print("\n📋 Prochaines étapes :")
        print("1. Lancez l'application avec: streamlit run app_enhanced.py")
        print("2. Testez le parcours interactif complet")
        print("3. Explorez les données locales enrichies")
        print("4. Configurez vos vraies clés API si nécessaire")

        # Proposition de lancement
        response = input("\n🚀 Voulez-vous lancer l'application maintenant ? (y/n): ")
        if response.lower() in ["y", "yes", "oui", "o"]:
            print("🚀 Lancement de l'application...")
            os.system("streamlit run app_enhanced.py")
    else:
        print("\n⚠️ Setup incomplet. Vérifiez les erreurs ci-dessus.")
        print("\n🔧 Tests complémentaires disponibles :")
        print("   python setup_enhanced.py --test-all")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-all":
        run_full_test()
    else:
        main()
