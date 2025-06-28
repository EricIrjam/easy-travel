#!/usr/bin/env python3
"""
Test Complet du Système Easy Travel
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_environment():
    """Test de l'environnement de base"""
    print("🔍 TEST ENVIRONNEMENT")
    print("=" * 30)

    # Vérifier Python
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Vérifier les fichiers essentiels
    essential_files = [
        "app_enhanced.py",
        "requirements.txt",
        ".env",
        "chatbot/bot.py",
        "services/local_data_service.py",
        "services/weather_service.py",
        "services/interactive_journey.py",
    ]

    missing_files = []
    for file in essential_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)

    return len(missing_files) == 0


def test_dependencies():
    """Test des dépendances Python"""
    print("\n🔧 TEST DÉPENDANCES")
    print("=" * 30)

    dependencies = [
        ("streamlit", "Interface web"),
        ("openai", "IA OpenAI"),
        ("langchain", "Framework LangChain"),
        ("pydantic", "Validation données"),
        ("dotenv", "Configuration"),
        ("requests", "Requêtes HTTP"),
    ]

    missing_deps = []
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} (module: {module})")
            missing_deps.append(module)

    if missing_deps:
        print(f"\n⚠️ Dépendances manquantes: {', '.join(missing_deps)}")
        print("💡 Installation: pip install -r requirements.txt")

    return len(missing_deps) == 0


def test_configuration():
    """Test de la configuration"""
    print("\n⚙️ TEST CONFIGURATION")
    print("=" * 30)

    try:
        from dotenv import load_dotenv

        load_dotenv()

        # Vérifier clé OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.startswith("sk-"):
            print("✅ Clé OpenAI configurée")
        else:
            print("⚠️ Clé OpenAI manquante ou invalide")

        # Vérifier clé météo
        weather_key = os.getenv("OPENWEATHER_API_KEY")
        if weather_key:
            print(f"✅ Clé météo: {weather_key[:10]}...")
        else:
            print("⚠️ Clé météo manquante (mode démo)")

        return True

    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False


def test_services():
    """Test des services Easy Travel"""
    print("\n🛠️ TEST SERVICES")
    print("=" * 30)

    services_tested = 0
    services_working = 0

    # Test service données locales
    try:
        from services.local_data_service import LocalDataService

        local_service = LocalDataService()
        print("✅ Service données locales")
        services_tested += 1
        services_working += 1

        # Test données Paris
        paris_info = local_service.get_city_info("paris")
        if paris_info:
            print(f"  • Données Paris: {paris_info.name}")
        else:
            print("  • Données Paris à initialiser")

    except Exception as e:
        print(f"❌ Service données locales: {e}")
        services_tested += 1

    # Test service météo
    try:
        from services.weather_service import WeatherService

        weather_service = WeatherService()
        print("✅ Service météo")
        services_tested += 1
        services_working += 1

    except Exception as e:
        print(f"❌ Service météo: {e}")
        services_tested += 1

    # Test parcours interactif
    try:
        from services.interactive_journey import InteractiveJourneyOrchestrator

        journey = InteractiveJourneyOrchestrator()
        print("✅ Parcours interactif")
        services_tested += 1
        services_working += 1

    except Exception as e:
        print(f"❌ Parcours interactif: {e}")
        services_tested += 1

    # Test chatbot
    try:
        from chatbot.bot import EasyTravelChatbot

        bot = EasyTravelChatbot()
        print("✅ Chatbot Easy Travel")
        services_tested += 1
        services_working += 1

    except Exception as e:
        print(f"❌ Chatbot: {e}")
        services_tested += 1

    return services_working == services_tested


def test_data_creation():
    """Test de création des données"""
    print("\n📊 TEST DONNÉES")
    print("=" * 30)

    # Créer les répertoires nécessaires
    data_dirs = ["data", "data/local_data", "data/user_plans", "logs"]
    for directory in data_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire: {directory}")

    try:
        from services.local_data_service import LocalDataService

        local_service = LocalDataService()

        # Initialiser les données si nécessaire
        cities = ["paris", "rome", "barcelone"]
        for city in cities:
            info = local_service.get_city_info(city)
            if info:
                print(f"✅ Données {city.title()}: {info.name}")
            else:
                print(f"⚠️ Données {city.title()} à créer")

        return True

    except Exception as e:
        print(f"❌ Erreur données: {e}")
        return False


def test_streamlit_app():
    """Test de l'application Streamlit"""
    print("\n🌐 TEST APPLICATION")
    print("=" * 30)

    try:
        # Vérifier que le fichier app_enhanced.py est syntaxiquement correct
        with open("app_enhanced.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Test de compilation basique
        compile(content, "app_enhanced.py", "exec")
        print("✅ Application Streamlit syntaxiquement correcte")

        # Vérifier les imports principaux dans l'app
        required_imports = [
            "import streamlit",
            "from chatbot.bot import EasyTravelChatbot",
            "from services.local_data_service import LocalDataService",
            "from services.weather_service import WeatherService",
        ]

        for imp in required_imports:
            if imp in content:
                print(
                    f"✅ Import détecté: {imp.split(' import ')[0].replace('from ', '').replace('import ', '')}"
                )
            else:
                print(f"⚠️ Import manquant: {imp}")

        return True

    except Exception as e:
        print(f"❌ Erreur application: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🚀 EASY TRAVEL - TEST COMPLET DU SYSTÈME")
    print("=" * 50)

    tests = [
        ("Environnement", test_environment),
        ("Dépendances", test_dependencies),
        ("Configuration", test_configuration),
        ("Services", test_services),
        ("Données", test_data_creation),
        ("Application", test_streamlit_app),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Erreur lors du test {name}: {e}")
            results.append((name, False))

    # Résumé des résultats
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"{name:15} : {status}")
        if result:
            passed += 1

    print(f"\n🎯 Score: {passed}/{total} tests réussis")

    if passed == total:
        print("\n🎉 SYSTÈME COMPLÈTEMENT OPÉRATIONNEL!")
        print("\n🚀 Pour lancer l'application:")
        print("   streamlit run app_enhanced.py")
        print("\n🌐 Accès: http://localhost:8501")
        print("\n💡 Fonctionnalités disponibles:")
        print("   • Parcours guidé interactif")
        print("   • Chat libre avec IA")
        print("   • Données locales enrichies")
        print("   • Informations météo")
        print("   • Génération de plans personnalisés")

    elif passed >= total * 0.8:
        print("\n⚠️ SYSTÈME MAJORITAIREMENT FONCTIONNEL")
        print("   Quelques composants à corriger")
        print("\n🚀 Vous pouvez essayer de lancer:")
        print("   streamlit run app_enhanced.py")

    else:
        print("\n❌ SYSTÈME NÉCESSITE DES CORRECTIONS")
        print("   Plusieurs composants ont échoué")
        print("\n💡 Actions recommandées:")
        print("   1. pip install -r requirements.txt")
        print("   2. Vérifier le fichier .env")
        print("   3. Relancer ce test")


if __name__ == "__main__":
    main()
