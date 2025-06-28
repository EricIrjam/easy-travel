#!/usr/bin/env python3
"""
Lanceur Simple Easy Travel
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """Lance l'application Easy Travel Enhanced"""

    print("🚀 Easy Travel Enhanced - Lancement")
    print("=" * 40)

    # Vérifier qu'on est dans le bon répertoire
    if not Path("app_enhanced.py").exists():
        print("❌ Erreur: app_enhanced.py non trouvé")
        print("   Placez-vous dans le répertoire easy_travel-chatbot")
        return

    print("✅ Application trouvée")

    # Vérifier Streamlit
    try:
        import streamlit

        print("✅ Streamlit disponible")
    except ImportError:
        print("❌ Streamlit non installé")
        print("   Installation en cours...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])

    # Créer les répertoires si nécessaire
    os.makedirs("data/local_data", exist_ok=True)
    os.makedirs("data/user_plans", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    print("✅ Répertoires de données créés")

    # Message de lancement
    print("\n🌐 Lancement de l'interface web...")
    print("   L'application va s'ouvrir dans votre navigateur")
    print("   URL: http://localhost:8501")
    print("\n💡 Fonctionnalités disponibles:")
    print("   • Parcours guidé interactif")
    print("   • Chat libre avec IA")
    print("   • Données météo temps réel")
    print("   • Recommandations personnalisées")
    print("\n   Appuyez sur Ctrl+C pour arrêter")
    print("=" * 40)

    # Lancer Streamlit
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app_enhanced.py",
                "--server.headless",
                "true",
                "--server.port",
                "8501",
            ]
        )
    except KeyboardInterrupt:
        print("\n\n👋 Application arrêtée")
    except Exception as e:
        print(f"\n❌ Erreur de lancement: {e}")
        print("\n🔧 Essayez manuellement:")
        print("   streamlit run app_enhanced.py")


if __name__ == "__main__":
    main()
