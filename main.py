# easy_travel_server_fixed.py - Compatible avec vos données JSON réelles
"""
Easy Travel API - Serveur HTTP adapté à votre structure de données
Compatible avec vos fichiers JSON existants
"""

import sys
import os
import json
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional
import threading
import webbrowser

print(f"🐍 Python {sys.version}")
print("🚀 Easy Travel - Serveur Compatible avec vos Données")

try:
    from weather_service import WeatherService
    WEATHER_SERVICE_AVAILABLE = True
    print("✅ Service météo chargé")
except ImportError as e:
    print(f"⚠️ Service météo non disponible: {e}")
    WEATHER_SERVICE_AVAILABLE = False
    
# Adaptateur pour vos données réelles
class EasyTravelDataAdapter:
    """Adaptateur pour lire vos fichiers JSON existants"""
    
    def __init__(self):
        self.destinations_data = self.load_real_destinations_data()
        self.conversation_history = {}
        
        # NOUVEAU: Initialisation du service météo
        if WEATHER_SERVICE_AVAILABLE:
            self.weather_service = WeatherService()
            print("🌤️ Service météo initialisé")
        else:
            self.weather_service = None
            print("🌤️ Service météo en mode fallback")
        
        print(f"🤖 Easy Travel Adapter initialisé - {len(self.destinations_data)} destinations")

    def load_real_destinations_data(self):
        """Charge VOS vraies données depuis data/local_data/"""
        destinations = {}
        
        # Vos dossiers de données
        possible_dirs = [
            "data/local_data",
            "data", 
            "./data/local_data",
            "./data"
        ]
        
        data_dir = None
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                data_dir = dir_path
                break
        
        if not data_dir:
            print("❌ Aucun dossier de données trouvé")
            return {}
        
        print(f"📁 Lecture des données depuis: {data_dir}")
        
        # Lecture de tous les fichiers JSON
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                city_name = filename.replace('.json', '').lower()
                try:
                    with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        destinations[city_name] = data
                    print(f"✅ {city_name.title()} chargé ({len(str(data))} caractères)")
                except Exception as e:
                    print(f"⚠️ Erreur {filename}: {e}")
        
        return destinations
    
    def process_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """Traite un message avec VOS données réelles"""
        
        # Sauvegarde dans l'historique
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "type": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Génération de la réponse avec VOS données
        response_text = self.generate_response_with_real_data(message.lower())
        suggestions = self.generate_suggestions(message.lower())
        
        # Sauvegarde de la réponse
        self.conversation_history[user_id].append({
            "type": "bot",
            "message": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "message": response_text,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "userProfile": {}
        }
    
    def generate_response_with_real_data(self, message_lower: str) -> str:
        """Génère une réponse avec VOS vraies données"""
        
        # NOUVEAU: Vérification MÉTÉO EN PREMIER
        if any(word in message_lower for word in ["météo", "temps", "climat", "température"]):
            return self.get_real_weather_response(message_lower)
        
        # Reste du code existant identique...
        detected_city = None
        for city in self.destinations_data.keys():
            if city in message_lower:
                detected_city = city
                break
        
        if detected_city:
            return self.get_real_city_response(detected_city, message_lower)
        elif any(word in message_lower for word in ["budget", "prix", "coût", "euro", "€", "argent"]):
            return self.get_budget_guide()
        # ... etc (garder le reste)
    
    def get_real_weather_response(self, message_lower: str) -> str:
        """Génère une réponse météo avec votre WeatherService"""
        
        # Détection de ville
        detected_city = None
        for city in self.destinations_data.keys():
            if city in message_lower:
                detected_city = city
                break
        
        if not detected_city:
            detected_city = "paris"
        
        # Utilise votre service météo
        if self.weather_service:
            try:
                weather_info = self.weather_service.get_current_weather(detected_city)
                if weather_info:
                    return f"""🌤️ **Météo Easy Travel - {detected_city.title()}** ☀️

    **🌡️ Conditions actuelles :**
    - **Température** : {weather_info.temperature:.1f}°C (ressenti {weather_info.feels_like:.1f}°C)
    - **Conditions** : {weather_info.description.title()}
    - **Humidité** : {weather_info.humidity}%
    - **Vent** : {weather_info.wind_speed:.1f} m/s
    - **Visibilité** : {weather_info.visibility:.1f} km

    **👕 Conseils vestimentaires :**
    {"• ❄️ Très froid - Manteau d'hiver" if weather_info.temperature < 5 else
    "• 🧥 Frais - Veste ou pull" if weather_info.temperature < 15 else  
    "• 👕 Agréable - T-shirt + veste légère" if weather_info.temperature < 25 else
    "• ☀️ Chaud - Vêtements légers"}

    **💡 Conseil Easy Travel :**
    *Météo temps réel pour votre voyage !*"""
            except Exception as e:
                print(f"Erreur météo: {e}")
        
        # Fallback
        return f"""🌤️ **Météo Easy Travel - {detected_city.title()}** 📱

    **🌡️ Conditions simulées :**
    - **Température** : 18°C
    - **Conditions** : Variable
    - **Humidité** : 65%

    **💡 Pour la météo temps réel :**
    *Configurez OPENWEATHER_API_KEY dans votre .env*"""

    def get_real_city_response(self, city: str, message_lower: str) -> str:
        """Génère une réponse avec VOS vraies données de ville"""
        city_data = self.destinations_data[city]
        city_title = city.title()
        
        response = f"🌍 **{city_title} - Guide Easy Travel Authentique** ✨\n\n"
        
        # ADAPTATION À VOTRE STRUCTURE
        
        # Informations générales (votre structure: city_info)
        if "city_info" in city_data:
            info = city_data["city_info"]
            response += f"**📍 Informations essentielles :**\n"
            response += f"• 🏛️ Pays : {info.get('country', 'N/A')}\n"
            response += f"• 💰 Monnaie : {info.get('currency', 'N/A')}\n"
            response += f"• 🗣️ Langues : {', '.join(info.get('languages', []))}\n"
            if 'emergency_numbers' in info:
                urgences = info['emergency_numbers']
                response += f"• 🚨 Urgences : "
                urgences_list = [f"{k} {v}" for k, v in urgences.items()]
                response += ", ".join(urgences_list[:2]) + "\n"
            response += "\n"
        
        # Attractions selon contexte (votre structure)
        if any(word in message_lower for word in ["attraction", "visite", "voir", "monument", "site"]) or len(message_lower.split()) <= 3:
            if "attractions" in city_data and city_data["attractions"]:
                response += f"**🎯 Attractions {city_title} :**\n"
                for i, attraction in enumerate(city_data["attractions"][:4], 1):
                    name = attraction.get("name", "Attraction")
                    category = attraction.get("category", "Site")
                    rating = attraction.get("rating", "N/A")
                    description = attraction.get("description", "")
                    
                    response += f"{i}. **{name}** ({category})\n"
                    response += f"   ⭐ {rating}/5 | 📍 {description[:60]}...\n"
                    
                    # Horaires si disponibles
                    if "opening_hours" in attraction:
                        hours = attraction["opening_hours"]
                        if isinstance(hours, dict):
                            # Exemple avec lundi
                            lundi = hours.get("lundi", hours.get("monday", "N/A"))
                            response += f"   ⏰ Exemple: Lundi {lundi}\n"
                    response += "\n"
        
        # Restaurants selon contexte (votre structure)
        if any(word in message_lower for word in ["restaurant", "manger", "cuisine", "food"]):
            if "restaurants" in city_data and city_data["restaurants"]:
                response += f"**🍽️ Restaurants {city_title} Authentiques :**\n"
                for i, restaurant in enumerate(city_data["restaurants"][:3], 1):
                    name = restaurant.get("name", "Restaurant")
                    cuisine = restaurant.get("cuisine_type", "Cuisine locale")
                    rating = restaurant.get("rating", "N/A")
                    price_range = restaurant.get("price_range", "€€")
                    specialties = restaurant.get("specialties", [])
                    
                    response += f"{i}. **{name}** ({cuisine})\n"
                    response += f"   ⭐ {rating}/5 | 💰 {price_range}"
                    if specialties:
                        response += f" | 🍴 {specialties[0]}"
                    response += "\n"
                response += "\n"
        
        # Transport selon contexte (votre structure)
        if any(word in message_lower for word in ["transport", "métro", "bus", "déplacer"]):
            if "transport" in city_data and city_data["transport"]:
                response += f"**🚇 Transport {city_title} :**\n"
                for transport in city_data["transport"][:2]:
                    transport_type = transport.get("type", "Transport")
                    cost = transport.get("cost", "N/A")
                    description = transport.get("description", "")
                    
                    response += f"• **{transport_type}** - {cost}\n"
                    if description:
                        response += f"  {description[:80]}...\n"
                    
                    # Tips si disponibles
                    if "tips" in transport:
                        tips = transport["tips"][:1]  # Premier conseil
                        for tip in tips:
                            response += f"  💡 {tip}\n"
                response += "\n"
        
        # Événements si disponibles (votre structure)
        if "events" in city_data and city_data["events"]:
            response += f"**🎭 Événements {city_title} :**\n"
            for event in city_data["events"][:2]:
                name = event.get("name", "Événement")
                description = event.get("description", "")
                start_date = event.get("start_date", "")
                response += f"• **{name}** - {description[:50]}...\n"
                if start_date:
                    response += f"  📅 {start_date}\n"
            response += "\n"
        
        # Conseils culturels (votre structure)
        if "city_info" in city_data and "cultural_etiquette" in city_data["city_info"]:
            etiquette = city_data["city_info"]["cultural_etiquette"][:2]
            response += f"**💡 Conseils locaux :**\n"
            for conseil in etiquette:
                response += f"• {conseil}\n"
            response += "\n"
        
        response += f"✨ *Données authentiques Easy Travel pour {city_title} !*"
        
        return response
    
    def get_budget_guide(self) -> str:
        return """💰 **Guide Budget Easy Travel** 📊

**🎯 Répartition optimale :**
• 🏨 Hébergement : 40%
• 🍽️ Restauration : 30%  
• 🎫 Activités : 20%
• 🚇 Transport : 10%

**💡 Astuces d'économie :**
• Réservez 2 mois à l'avance (-25%)
• Déjeuner dans les marchés (-40%)
• Pass touristiques (-30%)
• Visites gratuites le dimanche

**📊 Budgets quotidiens :**
• 💸 Économique : 40-60€
• 💼 Confort : 80-120€
• 🌟 Premium : 150-300€"""

    def get_weather_guide(self) -> str:
        return """🌤️ **Guide Météo Easy Travel** 📱

**📍 Planification intelligente :**
• Vérifiez 7 jours avant départ
• Apps météo locales recommandées
• Prévoyez plan B pour la pluie

**📅 Meilleures périodes :**
• 🌸 Printemps : Temps idéal, prix modérés
• ☀️ Été : Parfait mais foules
• 🍂 Automne : Excellent compromis
• ❄️ Hiver : Atmosphère unique, tarifs bas

**🎒 Kit météo universel :**
• Couches multiples
• Veste imperméable légère
• Chaussures confortables
• Parapluie compact"""

    def get_food_guide(self) -> str:
        return """🍽️ **Guide Gastronomique Easy Travel** 👨‍🍳

**🎯 Expériences authentiques :**

**🏆 Restaurants locaux :**
• Fréquentés par les habitants
• Évitez zones ultra-touristiques
• Réservez les tables populaires

**🥙 Street Food :**
• Immersion culturelle garantie
• Saveurs authentiques, prix mini
• Cherchez les files d'attente !

**💡 Conseils de Pro :**
• Déjeuner = meilleur rapport qualité/prix
• Goûtez 1 spécialité locale/jour
• Apps locales pour vrais avis
• Photographiez les cartes"""

    def get_transport_guide(self) -> str:
        return """🚗 **Transport Intelligent Easy Travel** 🚊

**✈️ Vols longue distance :**
• Réservez 6-8 semaines à l'avance
• Comparateurs : Skyscanner, Google Flights
• Dates flexibles = économies

**🚊 Transport local :**
• Pass journaliers souvent avantageux
• Apps officielles pour horaires
• Vélos partagés = découverte + sport
• Marche = quartiers authentiques

**💡 Pro Tips :**
• Pass touristiques incluent transport
• Évitez taxis en centre-ville
• Cartes offline indispensables
• Transport public = immersion locale"""

    def get_welcome_message(self) -> str:
        cities_list = ", ".join([city.title() for city in list(self.destinations_data.keys())[:6]])
        
        return f"""✈️ **Bienvenue sur Easy Travel !** 🌍

Je suis votre assistant voyage **avec VOS données authentiques** ! 🤖

**🚀 Mes capacités avec vos données :**
• 🗺️ **Données réelles** - Issues de vos fichiers JSON
• 💰 **Conseils budget** - Optimisation garantie
• 🏨 **Hébergements** - Toutes gammes
• 🍽️ **Gastronomie locale** - Vraies recommandations
• 🌤️ **Conseils météo** - Préparation optimale
• 🚗 **Transport** - Solutions pratiques

**🌍 Vos destinations disponibles :**
{cities_list}{"..." if len(self.destinations_data) > 6 else ""}

**✨ Exemples avec vos données :**
• *"Attractions à Paris"*
• *"Restaurants à {list(self.destinations_data.keys())[0].title()}"*  
• *"Transport à {list(self.destinations_data.keys())[1].title() if len(self.destinations_data) > 1 else 'Paris'}"*

**🎯 Spécialisé dans vos destinations !**
**🚀 Où voulez-vous voyager ?**"""

    def generate_suggestions(self, message_lower: str) -> List[str]:
        """Génère des suggestions basées sur vos données disponibles"""
        
        # Suggestions spécifiques par ville
        if "paris" in message_lower:
            return ["🗼 Tour Eiffel détails", "🍽️ L'As du Fallafel", "🚇 Métro parisien", "🎭 Événements Paris"]
        
        # Suggestions générales basées sur vos données
        available_cities = list(self.destinations_data.keys())
        if len(available_cities) >= 2:
            return [
                f"🗺️ Guide {available_cities[0].title()}",
                f"🍽️ Restaurants {available_cities[1].title() if len(available_cities) > 1 else available_cities[0].title()}",
                "💰 Optimiser budget",
                "🌤️ Conseils météo"
            ]
        else:
            return ["🗺️ Planifier voyage", "💰 Budget voyage", "🌤️ Météo destination", "🍽️ Gastronomie locale"]

# Reste du serveur HTTP identique...
# [Le code du serveur HTTP reste le même, on change juste l'instance]

class EasyTravelHandler(BaseHTTPRequestHandler):
    """Gestionnaire de requêtes HTTP pour Easy Travel"""
    
    def log_message(self, format, *args):
        """Logs personnalisés"""
        print(f"🌐 {datetime.now().strftime('%H:%M:%S')} - {format % args}")
    
    def do_GET(self):
        """Gestionnaire des requêtes GET"""
        if self.path == '/':
            self.send_api_info()
        elif self.path == '/api/health':
            self.send_health_check()
        elif self.path == '/api/destinations':
            self.send_destinations()
        elif self.path.startswith('/api/debug'):
            self.send_debug_info()
        else:
            self.send_not_found()
    
    def do_POST(self):
        """Gestionnaire des requêtes POST"""
        if self.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_not_found()
    
    def do_OPTIONS(self):
        """Gestionnaire CORS pour les requêtes OPTIONS"""
        self.send_cors_response()
    
    def send_cors_headers(self):
        """Ajoute les headers CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json_response(self, data: Dict, status_code: int = 200):
        """Envoie une réponse JSON avec CORS"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_cors_headers()
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_cors_response(self):
        """Réponse CORS pour les requêtes OPTIONS"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_api_info(self):
        """Page d'accueil de l'API"""
        info = {
            "service": "Easy Travel API",
            "version": "1.0.0 - Compatible avec vos données",
            "python_version": f"{sys.version.split()[0]}",
            "status": "🚀 Opérationnel",
            "data_source": "VOS fichiers JSON authentiques",
            "destinations_loaded": len(chatbot_adapter.destinations_data),
            "destinations_available": list(chatbot_adapter.destinations_data.keys()),
            "endpoints": {
                "chat": "POST /api/chat",
                "health": "GET /api/health",
                "destinations": "GET /api/destinations",
                "debug": "GET /api/debug"
            },
            "test_example": 'curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d \'{"message":"Attractions à Paris"}\''
        }
        self.send_json_response(info)
    
    def send_health_check(self):
        """Health check de l'API"""
        health = {
            "status": "healthy",
            "mode": "real_data",
            "python_version": f"{sys.version.split()[0]}",
            "timestamp": datetime.now().isoformat(),
            "destinations_count": len(chatbot_adapter.destinations_data),
            "active_conversations": len(chatbot_adapter.conversation_history),
            "data_source": "Fichiers JSON utilisateur"
        }
        self.send_json_response(health)
    
    def send_destinations(self):
        """Liste des destinations disponibles depuis VOS données"""
        destinations_info = {}
        for city, data in chatbot_adapter.destinations_data.items():
            city_title = city.title()
            destinations_info[city_title] = {
                "attractions_count": len(data.get("attractions", [])),
                "restaurants_count": len(data.get("restaurants", [])),
                "has_transport_info": "transport" in data,
                "has_events": "events" in data
            }
        
        result = {
            "destinations": list(destinations_info.keys()),
            "count": len(destinations_info),
            "details": destinations_info,
            "status": "success",
            "data_source": "Vos fichiers JSON authentiques"
        }
        self.send_json_response(result)
    
    def send_debug_info(self):
        """Informations de debug sur vos données"""
        debug_info = {
            "destinations_loaded": len(chatbot_adapter.destinations_data),
            "data_structure_analysis": {}
        }
        
        # Analyse de la structure de vos données
        for city, data in list(chatbot_adapter.destinations_data.items())[:2]:  # 2 premiers
            debug_info["data_structure_analysis"][city] = {
                "main_keys": list(data.keys()),
                "attractions_count": len(data.get("attractions", [])),
                "restaurants_count": len(data.get("restaurants", [])),
                "has_city_info": "city_info" in data,
                "sample_attraction": data.get("attractions", [{}])[0].get("name", "N/A") if data.get("attractions") else "N/A"
            }
        
        self.send_json_response(debug_info)
    
    def handle_chat(self):
        """Gestionnaire du chat avec VOS données"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                user_id = data.get('userId', 'default_user')
                
                if not message.strip():
                    raise ValueError("Message vide")
                
            except (json.JSONDecodeError, ValueError) as e:
                self.send_json_response({
                    "message": "😔 **Erreur de format**\n\nLe message doit être au format JSON avec un champ 'message'.",
                    "suggestions": ["🔄 Réessayer", "📚 Documentation"],
                    "status": "error",
                    "timestamp": datetime.now().isoformat()
                }, 400)
                return
            
            # Traitement avec VOS données réelles
            print(f"💬 Message reçu: {message[:50]}...")
            response = chatbot_adapter.process_message(message, user_id)
            print(f"✅ Réponse générée avec vos données ({len(response['message'])} caractères)")
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"❌ Erreur chat: {e}")
            self.send_json_response({
                "message": f"😔 **Erreur serveur Easy Travel**\n\nErreur: {str(e)}\n\nVos données sont chargées mais une erreur de traitement s'est produite.",
                "suggestions": ["🔄 Réessayer", "🔧 Debug", "📞 Support"],
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }, 500)
    
    def send_not_found(self):
        """Réponse 404"""
        self.send_json_response({
            "error": "Endpoint non trouvé",
            "available_endpoints": ["/", "/api/health", "/api/chat", "/api/destinations", "/api/debug"],
            "status": "error"
        }, 404)

# Instance globale de l'adaptateur pour VOS données
chatbot_adapter = EasyTravelDataAdapter()

def run_server(port=8000):
    """Lance le serveur HTTP"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, EasyTravelHandler)
    
    print(f"🚀 Easy Travel Server Compatible avec VOS données !")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🤖 Adaptateur: Compatible avec votre structure JSON")
    print(f"🗺️ Destinations chargées: {len(chatbot_adapter.destinations_data)}")
    print(f"📁 Vos villes: {', '.join([city.title() for city in chatbot_adapter.destinations_data.keys()])}")
    print("\n🔥 API Endpoints:")
    print(f"   GET  http://localhost:{port}/")
    print(f"   POST http://localhost:{port}/api/chat")
    print(f"   GET  http://localhost:{port}/api/destinations")
    print(f"   GET  http://localhost:{port}/api/debug")
    print("\n💡 Test avec vos données:")
    print(f'   curl -X POST http://localhost:{port}/api/chat -H "Content-Type: application/json" -d \'{{"message":"Attractions à Paris"}}\'')
    print("\n🛑 Arrêt: Ctrl+C")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur Easy Travel...")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()