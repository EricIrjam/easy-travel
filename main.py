from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration FastAPI
app = FastAPI(title="Easy Travel API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://easy-travel-front:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles


class ChatMessage(BaseModel):
    message: str
    userProfile: Optional[Dict[str, Any]] = {}
    conversationHistory: Optional[List[Dict[str, Any]]] = []


class ChatResponse(BaseModel):
    message: str
    suggestions: Optional[List[str]] = []
    userProfile: Optional[Dict[str, Any]] = {}


# Initialisation du service chatbot
CHATBOT_AVAILABLE = False
chatbot_service = None

# Tentative d'import du vrai chatbot
try:
    # Import depuis votre structure existante
    sys.path.append('/app')

    # Option 1: Si vous avez une classe EasyTravelBot
    if os.path.exists('/app/chatbot/bot.py'):
        from chatbot.bot import EasyTravelBot
        chatbot_service = EasyTravelBot()
        CHATBOT_AVAILABLE = True
        print("✅ Chatbot EasyTravel chargé avec succès")

    # Option 2: Si vous avez une fonction process_message
    elif os.path.exists('/app/app_enhanced.py'):
        import streamlit as st
        from app_enhanced import main as streamlit_main
        print("✅ Module Streamlit détecté - Adaptation nécessaire")

except Exception as e:
    print(f"⚠️  Impossible de charger le chatbot: {e}")
    print("🔄 Fonctionnement en mode démo")

# Fonctions de traitement


def process_with_real_chatbot(message: str, user_profile: dict = None) -> str:
    """Traite le message avec le vrai chatbot"""
    try:
        if CHATBOT_AVAILABLE and chatbot_service:
            # Adapter selon votre API de chatbot
            if hasattr(chatbot_service, 'process_message'):
                response = chatbot_service.process_message(
                    message, user_profile)
            elif hasattr(chatbot_service, 'chat'):
                response = chatbot_service.chat(message)
            elif hasattr(chatbot_service, 'get_response'):
                response = chatbot_service.get_response(message)
            else:
                # Essayer d'appeler directement
                response = chatbot_service(message)

            return str(response) if response else "Réponse du chatbot non disponible"
        else:
            return process_demo_message(message)

    except Exception as e:
        print(f"Erreur chatbot: {e}")
        return f"Désolé, une erreur est survenue: {str(e)}"


def process_demo_message(message: str) -> str:
    """Messages de démonstration enrichis"""
    message_lower = message.lower()

    demo_responses = {
        "paris": """🏛️ **Paris - La Ville Lumière**

✨ **Attractions recommandées :**
- 🗼 Tour Eiffel (29.40€) - Vue panoramique exceptionnelle
- 🖼️ Musée du Louvre (17€) - Art et culture mondiale  
- ⛪ Notre-Dame (gratuit) - Architecture gothique

🍽️ **Restaurants authentiques :**
- 🥙 L'As du Fallafel (8€) - Meilleur fallafel de Paris
- 🍷 Le Comptoir du Relais (35€) - Bistrot parisien typique

🚇 **Transport optimisé :**
- Pass Navigo semaine (22.80€) - Métro illimité
- Vélib' (5€/jour) - Vélos en libre-service

💰 **Budget total recommandé :** 150-300€ pour 3 jours""",

        "rome": """🏛️ **Rome - La Ville Éternelle**

✨ **Sites historiques :**
- 🏟️ Colisée (27€) - Amphithéâtre emblématique
- ⛪ Vatican (20€) - Chapelle Sixtine et art sacré
- ⛲ Fontaine de Trevi (gratuit) - Tradition des pièces

🍝 **Cuisine italienne :**
- 🍕 Da Enzo (25€) - Pizza authentique romaine
- 🍝 Trattoria Monti (30€) - Pâtes traditionnelles

🚇 **Transport local :**
- Pass Roma 3 jours (18€) - Métro et bus
- Marche à pied - Centre historique compact

💰 **Budget total recommandé :** 120-250€ pour 3 jours""",

        "budget": """💰 **Optimisation Budget Voyage**

🎯 **Répartition recommandée :**
- 40% Hébergement
- 30% Restauration  
- 20% Attractions et activités
- 10% Transport local

💡 **Astuces économies :**
- 🏨 Réserver à l'avance (-20%)
- 🍽️ Déjeuner dans les marchés locaux
- 🎫 Pass touristiques multi-attractions
- 🚶 Visites à pied gratuites

📊 **Exemples de budgets :**
- Budget serré : 50€/jour
- Confort : 100€/jour  
- Premium : 200€/jour"""
    }

    # Détection contextuelle
    if any(city in message_lower for city in ["paris", "tour eiffel", "louvre"]):
        return demo_responses["paris"]
    elif any(city in message_lower for city in ["rome", "colisée", "vatican"]):
        return demo_responses["rome"]
    elif any(word in message_lower for word in ["budget", "prix", "coût", "euro", "€"]):
        return demo_responses["budget"]
    elif "météo" in message_lower:
        return "🌤️ **Météo temps réel** : 22°C, ensoleillé ☀️\n\n📅 **Prévisions :**\n• Demain : 24°C ☀️\n• Après-demain : 21°C ⛅"
    else:
        return """✈️ **Bienvenue sur Easy Travel !**

Je peux vous aider à :
🗺️ Planifier votre itinéraire complet
💰 Optimiser votre budget voyage  
🏨 Trouver des hébergements
🍽️ Découvrir la gastronomie locale
🌤️ Vérifier la météo

**Essayez :** "Je veux visiter Paris avec 1000€" """

# Routes API


@app.get("/")
async def root():
    return {
        "message": "Easy Travel API is running!",
        "chatbot_status": "available" if CHATBOT_AVAILABLE else "demo_mode",
        "version": "1.0.0"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    try:
        # Traitement avec le vrai chatbot ou démo
        response_text = process_with_real_chatbot(
            chat_message.message,
            chat_message.userProfile
        )

        # Suggestions contextuelles
        suggestions = [
            "Recommande-moi des restaurants",
            "Quel temps fait-il ?",
            "Optimise mon budget",
            "Trouve des activités gratuites"
        ]

        return ChatResponse(
            message=response_text,
            suggestions=suggestions,
            userProfile=chat_message.userProfile
        )

    except Exception as e:
        print(f"Erreur API: {e}")
        return ChatResponse(
            message=f"😔 Une erreur est survenue: {str(e)}",
            suggestions=["Réessayer", "Contacter le support"]
        )


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "chatbot_available": CHATBOT_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/chatbot-status")
async def chatbot_status():
    return {
        "available": CHATBOT_AVAILABLE,
        "mode": "production" if CHATBOT_AVAILABLE else "demo",
        "service": str(type(chatbot_service)) if chatbot_service else None
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage Easy Travel API...")
    print(f"🤖 Chatbot: {'Disponible' if CHATBOT_AVAILABLE else 'Mode démo'}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
