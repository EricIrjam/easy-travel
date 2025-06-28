#!/bin/bash

echo "🚀 Lancement d'Easy Travel Enhanced"
echo "================================="

# Aller dans le répertoire du projet
cd /Users/eric/easy_travel-chatbot

# Activer l'environnement virtuel s'il existe
if [ -d ".venv" ]; then
    echo "📦 Activation de l'environnement virtuel..."
    source .venv/bin/activate
    echo "✅ Environnement virtuel activé"
fi

# Installer les dépendances si nécessaire
echo "📋 Vérification des dépendances..."
pip install -q -r requirements.txt

# Vérifier que les répertoires de données existent
echo "📁 Création des répertoires de données..."
mkdir -p data/local_data
mkdir -p data/user_plans
mkdir -p data/cache
mkdir -p logs

echo "✅ Préparation terminée"

# Lancer l'application Streamlit
echo ""
echo "🌐 Lancement de l'interface web..."
echo "   L'application va s'ouvrir dans votre navigateur"
echo "   URL: http://localhost:8501"
echo ""
echo "💡 Fonctionnalités disponibles:"
echo "   • Parcours guidé interactif"
echo "   • Chat libre avec IA"
echo "   • Données météo en temps réel"
echo "   • Recommandations personnalisées"
echo ""

# Démarrer Streamlit
streamlit run app_enhanced.py --server.headless true
