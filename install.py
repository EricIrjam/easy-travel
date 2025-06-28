#!/usr/bin/env python3
"""
Script de vérification et installation pour Easy Travel
"""

import subprocess
import sys
import os
from pathlib import Path


def install_requirements():
    """Installe les dépendances depuis requirements.txt"""
    requirements_path = Path(__file__).parent / "requirements.txt"

    if not requirements_path.exists():
        print("❌ Fichier requirements.txt non trouvé")
        return False

    print("📦 Installation des dépendances...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        )
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False


def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(
            f"❌ Python 3.8+ requis, version actuelle: {version.major}.{version.minor}"
        )
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def main():
    """Fonction principale"""
    print("🔧 Easy Travel - Installation et vérification")
    print("=" * 50)

    # Vérification Python
    if not check_python_version():
        return

    # Installation des dépendances
    if not install_requirements():
        return

    print("\n✅ Installation terminée !")
    print("🚀 Vous pouvez maintenant lancer: python launch_enhanced.py")


if __name__ == "__main__":
    main()
