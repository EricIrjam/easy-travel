#!/bin/bash

echo "🚀 Easy Travel - Lancement Final"
echo "================================"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app_enhanced.py" ]; then
    echo "❌ Erreur: Fichier app_enhanced.py non trouvé"
    echo "   Placez-vous dans le répertoire easy_travel-chatbot"
    exit 1
fi

echo "✅ Application Easy Travel détectée"

# Activer l'environnement virtuel
if [ -d ".venv" ]; then
    echo "🔧 Activation de l'environnement virtuel (.venv)..."
    source .venv/bin/activate
    echo "✅ Environnement virtuel activé"
else
    echo "⚠️ Environnement virtuel .venv non trouvé"
    echo "   Utilisation de l'environnement système"
fi

# Installer/mettre à jour les dépendances
echo "📦 Vérification des dépendances..."
pip install -q -r requirements.txt
echo "✅ Dépendances installées"

# Créer les répertoires nécessaires
echo "📁 Création des répertoires de données..."
mkdir -p data/local_data
mkdir -p data/user_plans  
mkdir -p logs
echo "✅ Répertoires créés"

# Vérifier la configuration
if [ -f ".env" ]; then
    echo "✅ Configuration .env trouvée"
else
    echo "⚠️ Fichier .env manquant"
    echo "   L'application fonctionnera en mode démo"
fi

echo ""
echo "🌐 Lancement de l'interface Easy Travel..."
echo "   L'application va s'ouvrir dans votre navigateur"
echo "   URL: http://localhost:8501"
echo ""
echo "💡 Fonctionnalités disponibles:"
echo "   • Parcours guidé interactif"
echo "   • Chat libre avec IA"
echo "   • Données locales enrichies"
echo "   • Informations météo temps réel"
echo "   • Génération de plans personnalisés"
echo ""
echo "🔄 Pour arrêter: Ctrl+C"
echo "================================"

# Lancer Streamlit
streamlit run app_enhanced.py
