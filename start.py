#!/usr/bin/env python3
"""
Easy Travel - Test final et lancement de l'application enrichie
"""

import subprocess
import sys
import os
from pathlib import Path


def run_demo():
    """Lance la démonstration des enrichissements"""
    print("🎬 Lancement de la démonstration...")
    try:
        subprocess.run(
            [sys.executable, "demo_enrichissements.py"], cwd=Path(__file__).parent
        )
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        return False


def install_dependencies():
    """Installe les dépendances si nécessaire"""
    print("📦 Vérification des dépendances...")
    try:
        subprocess.run([sys.executable, "install.py"], cwd=Path(__file__).parent)
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False


def launch_streamlit_app():
    """Lance l'application Streamlit enrichie"""
    app_path = Path(__file__).parent / "app_enhanced.py"

    if not app_path.exists():
        print("❌ Fichier app_enhanced.py non trouvé")
        return False

    print("🚀 Lancement de Easy Travel - Interface Enrichie")
    print("📱 L'application va s'ouvrir dans votre navigateur")
    print("🔄 Pour arrêter: Ctrl+C dans ce terminal")
    print("=" * 60)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                "--server.port",
                "8501",
                "--server.address",
                "localhost",
            ]
        )
        return True
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée par l'utilisateur")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False


def show_usage_guide():
    """Affiche un guide d'utilisation"""
    print("\n" + "=" * 60)
    print("📖 GUIDE D'UTILISATION - EASY TRAVEL ENRICHI")
    print("=" * 60)

    print("\n🎯 FONCTIONNALITÉS PRINCIPALES:")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ 1. PARCOURS GUIDÉ INTERACTIF                           │")
    print("│    • Questions progressives et personnalisées          │")
    print("│    • Collecte structurée des préférences               │")
    print("│    • Interface adaptative avec widgets avancés         │")
    print("│                                                         │")
    print("│ 2. DONNÉES LOCALES ENRICHIES                           │")
    print("│    • Attractions avec détails complets                 │")
    print("│    • Restaurants avec spécialités locales              │")
    print("│    • Informations transport et culture                 │")
    print("│                                                         │")
    print("│ 3. SERVICE MÉTÉO INTÉGRÉ                               │")
    print("│    • Météo actuelle et prévisions                      │")
    print("│    • Conseils adaptés aux conditions                   │")
    print("│    • Recommandations activités selon météo             │")
    print("│                                                         │")
    print("│ 4. INTERFACE MODERNE                                   │")
    print("│    • Sidebar contextuelle avec infos utiles            │")
    print("│    • Onglets pour différents modes d'utilisation       │")
    print("│    • Progression visuelle du parcours                  │")
    print("└─────────────────────────────────────────────────────────┘")

    print("\n🧭 NAVIGATION DANS L'APPLICATION:")
    print("• Mode 'Parcours Guidé': Suivez les étapes interactives")
    print("• Mode 'Chat Libre': Conversation naturelle avec l'IA")
    print("• Mode 'Données Utilisateur': Consultez profil et historique")
    print("• Sidebar: Météo en temps réel et infos locales")

    print("\n💡 CONSEILS D'UTILISATION:")
    print("• Commencez par le parcours guidé pour une expérience optimale")
    print("• Les données locales sont préchargées pour Paris, Rome, Barcelone")
    print("• Le mode démo fonctionne sans clés API (données simulées)")
    print("• Configurez vos clés API dans .env pour des données réelles")

    print("\n🔧 CONFIGURATION AVANCÉE:")
    print("• OPENAI_API_KEY: Pour les conversations IA complètes")
    print("• OPENWEATHER_API_KEY: Pour la météo en temps réel")
    print("• MONGODB_URI: Pour la persistance des données utilisateur")


def main():
    """Fonction principale"""
    print("✈️ EASY TRAVEL - LANCEMENT ENRICHI")
    print("=" * 60)

    # Choix utilisateur
    print("\nQue souhaitez-vous faire ?")
    print("1. 🎬 Voir la démonstration des enrichissements")
    print("2. 📦 Installer les dépendances")
    print("3. 🚀 Lancer l'application directement")
    print("4. 📖 Voir le guide d'utilisation")
    print("5. 🎯 Tout faire (recommandé)")

    try:
        choice = input("\nVotre choix (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
        return

    if choice == "1":
        run_demo()
    elif choice == "2":
        install_dependencies()
    elif choice == "3":
        launch_streamlit_app()
    elif choice == "4":
        show_usage_guide()
    elif choice == "5":
        # Processus complet
        print("\n🎯 Processus complet d'initialisation...")

        print("\n1/4 - Installation des dépendances...")
        if install_dependencies():
            print("✅ Dépendances installées")

        print("\n2/4 - Démonstration des fonctionnalités...")
        if run_demo():
            print("✅ Démonstration terminée")

        print("\n3/4 - Guide d'utilisation...")
        show_usage_guide()

        print("\n4/4 - Lancement de l'application...")
        input("Appuyez sur Entrée pour lancer l'application Streamlit...")
        launch_streamlit_app()
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
