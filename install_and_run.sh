#!/bin/bash
# Script de démarrage et installation Easy Travel

echo "🚀 Easy Travel - Installation et Lancement"
echo "=========================================="

# Vérifier si nous sommes dans le bon répertoire
if [ ! -f "app_enhanced.py" ]; then
    echo "❌ Erreur: Fichier app_enhanced.py non trouvé"
    echo "   Placez-vous dans le répertoire easy_travel-chatbot"
    exit 1
fi

echo "✅ Répertoire du projet détecté"

# Créer un environnement virtuel si nécessaire
if [ ! -d ".venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source .venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer les répertoires nécessaires
echo "📁 Création des répertoires de données..."
mkdir -p data/local_data
mkdir -p data/user_plans
mkdir -p logs

# Vérifier la configuration
echo "⚙️ Vérification de la configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️ Fichier .env manquant"
    echo "   Créez un fichier .env avec vos clés API"
else
    echo "✅ Configuration .env trouvée"
fi

# Test rapide des imports
echo "🧪 Test des imports..."
python3 -c "
try:
    import streamlit
    print('✅ Streamlit OK')
except ImportError:
    print('❌ Streamlit manquant')

try:
    import openai
    print('✅ OpenAI OK')
except ImportError:
    print('❌ OpenAI manquant')

try:
    from chatbot.bot import EasyTravelChatbot
    print('✅ Chatbot Easy Travel OK')
except ImportError as e:
    print(f'❌ Chatbot: {e}')
"

echo ""
echo "🎉 Installation terminée!"
echo ""
echo "🚀 Pour lancer l'application:"
echo "   streamlit run app_enhanced.py"
echo ""
echo "🌐 L'application s'ouvrira sur:"
echo "   http://localhost:8501"
echo ""
echo "💡 Fonctionnalités disponibles:"
echo "   • Parcours guidé pour planifier votre voyage"
echo "   • Chat libre avec assistant IA"
echo "   • Données locales authentiques (attractions, restaurants)"
echo "   • Informations météo en temps réel"
echo "   • Génération de plans personnalisés"
echo ""
echo "📚 Documentation complète dans README.md"
echo "=========================================="
