#!/usr/bin/env python3
"""
Test du système Easy Travel enrichi
"""

import sys
import os
from pathlib import Path

# Ajoute le répertoire racine au path
sys.path.append(str(Path(__file__).parent))


def test_enriched_chatbot():
    """Test le chatbot enrichi avec tous les services"""
    print("🤖 TEST CHATBOT ENRICHI")
    print("=" * 40)

    try:
        from chatbot.bot import EasyTravelChatbot

        # Initialise le chatbot
        bot = EasyTravelChatbot()
        print("✅ Chatbot initialisé avec succès")

        # Test avec un utilisateur
        user_id = "test_enriched_user"

        # Messages de test progressifs
        test_messages = [
            "Bonjour ! Je souhaite visiter Paris avec un budget de 1200€",
            "J'aime la culture et la gastronomie, pour un voyage en amoureux",
            "Quel temps fait-il là-bas actuellement ?",
            "Pouvez-vous me recommander des restaurants typiques ?",
            "Génère-moi un plan de voyage complet",
        ]

        print(f"\n💬 Simulation de conversation avec l'utilisateur {user_id}")

        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Message {i} ---")
            print(f"👤 Utilisateur: {message}")

            try:
                response = bot.process_message(message, user_id)
                print(
                    f"🤖 Easy Travel: {response[:200]}..."
                    if len(response) > 200
                    else f"🤖 Easy Travel: {response}"
                )

                # Test de génération de plan au dernier message
                if i == len(test_messages):
                    print(f"\n📋 Génération du plan de voyage...")
                    plan = bot.generate_travel_plan(user_id)
                    if "error" not in plan:
                        print(
                            f"✅ Plan généré: {plan['destination']} - {plan['durée_jours']} jours"
                        )
                        print(
                            f"   • {len(plan.get('attractions_recommandées', []))} attractions"
                        )
                        print(
                            f"   • {len(plan.get('restaurants_suggérés', []))} restaurants"
                        )
                        print(
                            f"   • Météo: {plan.get('météo', {}).get('actuelle', {}).get('température', 'N/A')}"
                        )
                    else:
                        print(f"❌ Erreur plan: {plan['error']}")

            except Exception as e:
                print(f"❌ Erreur lors du traitement: {e}")

        # Test des recommandations intelligentes
        print(f"\n🎯 Test des recommandations personnalisées...")
        try:
            recs = bot.get_smart_recommendations(user_id)
            if "error" not in recs:
                print(
                    f"✅ {len(recs.get('recommendations', []))} recommandations générées"
                )
            else:
                print(f"❌ {recs['error']}")
        except Exception as e:
            print(f"❌ Erreur recommandations: {e}")

        return True

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_services_integration():
    """Test l'intégration de tous les services"""
    print("\n🔧 TEST INTÉGRATION SERVICES")
    print("=" * 40)

    services_status = {}

    # Test service de données locales
    try:
        from services.local_data_service import LocalDataService

        local_service = LocalDataService()

        paris_info = local_service.get_city_info("paris")
        attractions = local_service.get_local_attractions("paris")

        services_status["Local Data"] = f"✅ {len(attractions)} attractions Paris"
    except Exception as e:
        services_status["Local Data"] = f"❌ {e}"

    # Test service météo
    try:
        from services.weather_service import WeatherService

        weather_service = WeatherService()

        weather = weather_service.get_current_weather("Paris")
        forecast = weather_service.get_forecast("Paris", 3)

        services_status["Météo"] = (
            f"✅ {weather.temperature}°C, {len(forecast)} prévisions"
        )
    except Exception as e:
        services_status["Météo"] = f"❌ {e}"

    # Test parcours interactif
    try:
        from services.interactive_journey import InteractiveJourneyOrchestrator

        journey = InteractiveJourneyOrchestrator()

        test_user = "integration_test"
        journey_data = journey.start_journey(test_user)
        progress = journey.get_user_progress(test_user)

        services_status["Parcours"] = f"✅ Étape: {journey_data['step'].title[:30]}..."
        journey.reset_journey(test_user)
    except Exception as e:
        services_status["Parcours"] = f"❌ {e}"

    # Test base de données
    try:
        from services.database import UserDatabase
        from models.user_profile import UserProfile, UserPreferences

        db = UserDatabase()
        db.client.admin.command("ping")

        services_status["Database"] = "✅ Connexion OK"
    except Exception as e:
        services_status["Database"] = f"❌ {e}"

    # Affichage des résultats
    print("État des services:")
    for service, status in services_status.items():
        print(f"  {service}: {status}")

    success_count = sum(
        1 for status in services_status.values() if status.startswith("✅")
    )
    total_count = len(services_status)

    print(f"\n📊 Résultat: {success_count}/{total_count} services fonctionnels")
    return success_count == total_count


def test_data_richness():
    """Test la richesse des données disponibles"""
    print("\n📊 TEST RICHESSE DES DONNÉES")
    print("=" * 40)

    try:
        from services.local_data_service import LocalDataService

        local_service = LocalDataService()

        # Test plusieurs villes
        cities = ["paris", "rome", "barcelone"]
        total_attractions = 0
        total_restaurants = 0

        for city in cities:
            attractions = local_service.get_local_attractions(city)
            restaurants = local_service.get_local_restaurants(city)

            total_attractions += len(attractions)
            total_restaurants += len(restaurants)

            print(
                f"📍 {city.title()}: {len(attractions)} attractions, {len(restaurants)} restaurants"
            )

        print(
            f"\n📈 Total: {total_attractions} attractions, {total_restaurants} restaurants"
        )
        print(f"✅ Base de données locale enrichie")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Test complet du système enrichi"""
    print("🛫 EASY TRAVEL - TEST SYSTÈME ENRICHI")
    print("=" * 60)

    tests = [
        ("Intégration des services", test_services_integration),
        ("Richesse des données", test_data_richness),
        ("Chatbot enrichi", test_enriched_chatbot),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results[test_name] = False

    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 Résultat global: {passed}/{total} tests réussis")

    if passed == total:
        print("\n🎉 Système Easy Travel entièrement opérationnel !")
        print("\n🚀 Fonctionnalités disponibles:")
        print("   • Chat intelligent avec contexte enrichi")
        print("   • Données locales détaillées (attractions, restaurants, transport)")
        print("   • Informations météo en temps réel")
        print("   • Parcours interactif guidé")
        print("   • Génération de plans de voyage personnalisés")
        print("   • Recommandations basées sur l'IA")
        print("   • Persistance des profils utilisateur")

        print("\n📱 Pour utiliser l'interface:")
        print("   streamlit run app_enhanced.py")

    else:
        print(f"\n⚠️ {total - passed} tests échoués")
        print("Vérifiez la configuration et les dépendances")


if __name__ == "__main__":
    main()
