# main.py - Easy Travel Chatbot Complet avec tous les services
"""
Easy Travel API - Serveur HTTP intégré avec tous vos services
Compatible avec votre frontend existant sur les mêmes URLs
"""

import sys
import os
import json
import urllib.parse
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional
import threading
import re

print(f"🐍 Python {sys.version}")
print("🚀 Easy Travel - Chatbot Complet avec tous les services")

# === IMPORTS DES SERVICES ===
try:
    # Services météo et données locales
    import requests
    from dataclasses import dataclass
    
    @dataclass
    class WeatherInfo:
        temperature: float
        humidity: int
        description: str
        feels_like: float
        wind_speed: float
        visibility: int
        uv_index: Optional[float] = None
        sunrise: Optional[str] = None
        sunset: Optional[str] = None

    class WeatherService:
        def __init__(self):
            self.api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
            self.base_url = "http://api.openweathermap.org/data/2.5"

        def get_current_weather(self, city: str, country_code: str = "") -> Optional[WeatherInfo]:
            location = f"{city},{country_code}" if country_code else city
            try:
                url = f"{self.base_url}/weather"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "fr",
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return WeatherInfo(
                        temperature=data["main"]["temp"],
                        humidity=data["main"]["humidity"],
                        description=data["weather"][0]["description"],
                        feels_like=data["main"]["feels_like"],
                        wind_speed=data["wind"]["speed"],
                        visibility=data.get("visibility", 0) / 1000,
                        sunrise=datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                        sunset=datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
                    )
            except Exception as e:
                print(f"Erreur météo pour {city}: {e}")
                return self._get_mock_weather(city)

        def _get_mock_weather(self, city: str) -> WeatherInfo:
            mock_data = {
                "paris": WeatherInfo(18.5, 65, "Nuageux", 20.1, 3.2, 8.5, sunrise="07:30", sunset="20:45"),
                "rome": WeatherInfo(24.3, 45, "Ensoleillé", 26.1, 2.1, 12.0, sunrise="06:45", sunset="21:15"),
                "lisbonne": WeatherInfo(21.8, 55, "Ensoleillé", 23.2, 2.8, 11.5, sunrise="07:00", sunset="20:30"),
                "barcelone": WeatherInfo(22.1, 70, "Partiellement nuageux", 24.5, 1.8, 9.2, sunrise="06:30", sunset="20:00"),
                "singapour": WeatherInfo(28.0, 85, "Chaud et humide", 32.0, 1.5, 8.0, sunrise="07:00", sunset="19:00"),
                "tokyo": WeatherInfo(22.0, 70, "Variable", 24.0, 2.0, 10.0, sunrise="05:30", sunset="18:30"),
            }
            return mock_data.get(city.lower(), WeatherInfo(20.0, 60, "Temps variable", 21.0, 2.5, 10.0))

        def get_travel_weather_advice(self, weather: WeatherInfo, activities: List[str]) -> List[str]:
            advice = []
            if weather.temperature < 10:
                advice.append("🧥 Pensez à emporter des vêtements chauds")
            elif weather.temperature > 30:
                advice.append("🌞 Température élevée, hydratez-vous bien")
            
            if weather.humidity > 80:
                advice.append("💧 Forte humidité, vêtements respirants recommandés")
            
            if "plage" in activities and weather.temperature < 20:
                advice.append("🏖️ Température fraîche pour la plage, pensez à un coupe-vent")
            
            if "nature" in activities and "pluie" in weather.description:
                advice.append("🌧️ Météo défavorable pour les activités nature")
            
            return advice if advice else ["☀️ Conditions météo favorables pour votre voyage"]

    # Service de recommandations
    class TravelRecommendationEngine:
        def __init__(self):
            self.google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
            
            # Base de données des destinations populaires
            self.destinations_db = {
                "europe": {
                    "paris": {
                        "climate": "temperate",
                        "budget": "medium",
                        "activities": ["culture", "gastronomie", "musées"],
                        "best_months": ["avril", "mai", "septembre", "octobre"]
                    },
                    "rome": {
                        "climate": "mediterranean", 
                        "budget": "medium",
                        "activities": ["culture", "histoire", "gastronomie", "art"],
                        "best_months": ["avril", "mai", "juin", "septembre"]
                    },
                    "barcelone": {
                        "climate": "mediterranean",
                        "budget": "medium", 
                        "activities": ["plage", "culture", "architecture", "gastronomie"],
                        "best_months": ["mai", "juin", "septembre", "octobre"]
                    },
                    "lisbonne": {
                        "climate": "atlantic",
                        "budget": "low",
                        "activities": ["culture", "histoire", "tramway", "fado"],
                        "best_months": ["avril", "mai", "juin", "septembre"]
                    }
                },
                "asie": {
                    "tokyo": {
                        "climate": "subtropical",
                        "budget": "high",
                        "activities": ["culture", "technologie", "gastronomie", "temples"]
                    },
                    "singapour": {
                        "climate": "tropical",
                        "budget": "high",
                        "activities": ["modernité", "gastronomie", "shopping", "multiculturalisme"]
                    },
                    "bangkok": {
                        "climate": "tropical",
                        "budget": "low", 
                        "activities": ["culture", "temples", "street food", "marchés"]
                    }
                }
            }

        def get_personalized_recommendations(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Génère des recommandations personnalisées"""
            recommendations = []
            
            for region, destinations in self.destinations_db.items():
                for dest_name, dest_info in destinations.items():
                    score = self._calculate_destination_score(dest_info, user_preferences)
                    
                    if score > 0.3:  # Seuil minimum
                        recommendations.append({
                            "destination": dest_name.title(),
                            "region": region,
                            "score": round(score, 2),
                            "reason": self._generate_recommendation_reason(dest_info, user_preferences),
                            "estimated_budget": self._estimate_budget(dest_info["budget"]),
                            "best_activities": dest_info["activities"][:3],
                            "climate": dest_info["climate"],
                            "best_months": dest_info.get("best_months", [])
                        })
            
            # Trie par score et retourne le top
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            return recommendations[:5]

        def _calculate_destination_score(self, destination: Dict[str, Any], preferences: Dict[str, Any]) -> float:
            """Calcule un score de compatibilité"""
            score = 0.0
            
            # Score basé sur les activités préférées
            dest_activities = set(destination["activities"])
            user_activities = set(preferences.get("preferred_activities", []))
            
            if user_activities:
                activity_match = len(dest_activities.intersection(user_activities)) / len(user_activities)
                score += activity_match * 0.4
            else:
                score += 0.2
            
            # Score basé sur le budget
            budget_range = preferences.get("budget_range", "medium")
            budget_compatibility = self._calculate_budget_compatibility(destination["budget"], budget_range)
            score += budget_compatibility * 0.3
            
            # Score basé sur le climat préféré
            if preferences.get("preferred_climate") == destination["climate"]:
                score += 0.2
            else:
                score += 0.1
            
            return min(score, 1.0)

        def _calculate_budget_compatibility(self, dest_budget: str, user_budget: str) -> float:
            """Calcule la compatibilité budgétaire"""
            compatibility_matrix = {
                ("low", "low"): 1.0,
                ("low", "medium"): 0.8,
                ("low", "high"): 0.6,
                ("medium", "low"): 0.3,
                ("medium", "medium"): 1.0,
                ("medium", "high"): 0.9,
                ("high", "low"): 0.1,
                ("high", "medium"): 0.4,
                ("high", "high"): 1.0,
            }
            return compatibility_matrix.get((dest_budget, user_budget), 0.5)

        def _generate_recommendation_reason(self, destination: Dict[str, Any], preferences: Dict[str, Any]) -> str:
            """Génère une raison personnalisée pour la recommandation"""
            reasons = []
            
            dest_activities = set(destination["activities"])
            user_activities = set(preferences.get("preferred_activities", []))
            matching_activities = dest_activities.intersection(user_activities)
            
            if matching_activities:
                reasons.append(f"Parfait pour {', '.join(matching_activities)}")
            
            budget_texts = {
                "low": "budget économique",
                "medium": "budget modéré", 
                "high": "budget généreux"
            }
            
            budget = preferences.get("budget_range", "medium")
            if budget in budget_texts:
                reasons.append(f"Adapté à votre {budget_texts[budget]}")
            
            return " • ".join(reasons) if reasons else "Destination populaire et variée"

        def _estimate_budget(self, dest_budget_category: str) -> str:
            """Estime le budget pour la destination"""
            budget_estimates = {
                "low": "400-800€ pour 7 jours",
                "medium": "800-1500€ pour 7 jours",
                "high": "1500-2500€ pour 7 jours",
            }
            return budget_estimates.get(dest_budget_category, "Budget à définir")

    WEATHER_SERVICE_AVAILABLE = True
    RECOMMENDATION_ENGINE_AVAILABLE = True
    print("✅ Services météo et recommandations chargés")
    
except ImportError as e:
    print(f"⚠️ Services non disponibles: {e}")
    WEATHER_SERVICE_AVAILABLE = False
    RECOMMENDATION_ENGINE_AVAILABLE = False

# === CLASSE PRINCIPALE EASY TRAVEL ===
class EasyTravelChatbot:
    """Chatbot Easy Travel complet avec tous les services intégrés"""
    
    def __init__(self):
        self.destinations_data = self.load_destinations_data()
        self.conversation_history = {}
        
        # Initialisation des services
        if WEATHER_SERVICE_AVAILABLE:
            self.weather_service = WeatherService()
            print("🌤️ Service météo initialisé")
        else:
            self.weather_service = None
            print("🌤️ Service météo en mode fallback")
        
        if RECOMMENDATION_ENGINE_AVAILABLE:
            self.recommendation_engine = TravelRecommendationEngine()
            print("🎯 Moteur de recommandations initialisé")
        else:
            self.recommendation_engine = None
            print("🎯 Moteur de recommandations en mode fallback")
        
        print(f"🤖 Easy Travel Chatbot initialisé - {len(self.destinations_data)} destinations")

    def load_destinations_data(self):
        """Charge vos vraies données depuis data/local_data/"""
        destinations = {}
        
        possible_dirs = [
            "data/local_data",
            "data", 
            "./data/local_data",
            "./data",
            "../data/local_data",
            "../data"
        ]
        
        data_dir = None
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                data_dir = dir_path
                break
        
        if not data_dir:
            print("❌ Aucun dossier de données trouvé - utilisation données intégrées")
            return self._get_fallback_data()
        
        print(f"📁 Lecture des données depuis: {data_dir}")
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                city_name = filename.replace('.json', '').lower()
                try:
                    with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        destinations[city_name] = data
                    print(f"✅ {city_name.title()} chargé")
                except Exception as e:
                    print(f"⚠️ Erreur {filename}: {e}")
        
        return destinations if destinations else self._get_fallback_data()

    def _get_fallback_data(self):
        """Données de fallback si les fichiers ne sont pas trouvés"""
        return {
            "paris": {
                "city_info": {
                    "name": "Paris",
                    "country": "France",
                    "currency": "EUR",
                    "languages": ["Français", "Anglais"],
                    "emergency_numbers": {"Police": "17", "Pompiers": "18"},
                    "tipping_culture": "Service compris, 5-10% si satisfait"
                },
                "attractions": [
                    {
                        "name": "Tour Eiffel",
                        "category": "Monument",
                        "description": "Symbole emblématique de Paris",
                        "rating": 4.4,
                        "price_level": 2
                    }
                ],
                "restaurants": [
                    {
                        "name": "L'As du Fallafel",
                        "cuisine_type": "Moyen-Oriental",
                        "description": "Meilleur falafel du Marais",
                        "rating": 4.3,
                        "price_range": "€€"
                    }
                ]
            }
        }

    def process_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """Traite un message utilisateur avec IA avancée"""
        
        # Sauvegarde dans l'historique
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "type": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Analyse intelligente du message
        analysis = self._analyze_message(message.lower())
        
        # Génération de réponse contextuelle
        response_text = self._generate_smart_response(message.lower(), analysis, user_id)
        suggestions = self._generate_smart_suggestions(message.lower(), analysis)
        
        # Extraction et sauvegarde des préférences
        preferences = self._extract_user_preferences(message, user_id)
        
        # Sauvegarde de la réponse
        self.conversation_history[user_id].append({
            "type": "bot",
            "message": response_text,
            "timestamp": datetime.now().isoformat(),
            "preferences_detected": preferences
        })
        
        return {
            "message": response_text,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "userProfile": self._get_user_profile(user_id),
            "context": analysis
        }

    def _analyze_message(self, message_lower: str) -> Dict[str, Any]:
        """Analyse intelligente du message utilisateur"""
        analysis = {
            "intent": "general",
            "entities": {
                "cities": [],
                "activities": [],
                "budget_indicators": [],
                "time_indicators": [],
                "preferences": []
            },
            "sentiment": "neutral",
            "complexity": "simple"
        }
        
        # Détection des villes (plus précise)
        detected_cities = []
        for city in self.destinations_data.keys():
            # Détection exacte et avec variantes
            city_variants = [city, city.title(), city.upper()]
            if any(variant in message_lower for variant in city_variants):
                detected_cities.append(city)
        
        # Ajouter aussi les variantes sans accents ou orthographes communes
        city_mappings = {
            "paris": ["paris", "paname"],
            "rome": ["rome", "roma"],
            "barcelone": ["barcelone", "barcelona", "bcn"],
            "lisbonne": ["lisbonne", "lisbon", "lisboa"],
            "amsterdam": ["amsterdam", "adam"],
            "sydney": ["sydney", "sid"],
            "singapour": ["singapour", "singapore", "sing"],
            "tokyo": ["tokyo", "tokio"]
        }
        
        for city, variants in city_mappings.items():
            if city in self.destinations_data and any(variant in message_lower for variant in variants):
                if city not in detected_cities:
                    detected_cities.append(city)
        
        analysis["entities"]["cities"] = detected_cities
        
        # Détection d'activités
        activity_keywords = {
            "culture": ["musée", "monument", "histoire", "art", "culture", "patrimoine", "museum"],
            "gastronomie": ["restaurant", "manger", "cuisine", "food", "gastronomie", "spécialité", "resto"],
            "nature": ["nature", "parc", "randonnée", "montagne", "plage", "mer"],
            "shopping": ["shopping", "boutique", "marché", "achats"],
            "nightlife": ["bar", "club", "sortie", "nuit", "concert", "nightlife"],
            "transport": ["transport", "métro", "metro", "bus", "train", "avion", "déplacement"]
        }
        
        for activity, keywords in activity_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                analysis["entities"]["activities"].append(activity)
        
        # Détection d'indicateurs de budget
        budget_keywords = ["budget", "prix", "coût", "euro", "€", "cher", "économique", "gratuit", "argent"]
        analysis["entities"]["budget_indicators"] = [word for word in budget_keywords if word in message_lower]
        
        # Détection d'intention (ordre TRÈS important - du plus spécifique au plus général)
        
        # 1. MÉTÉO (priorité absolue) - détection améliorée
        weather_keywords = ["météo", "meteo", "temps", "climat", "température", "pluie", "soleil", "weather"]
        if any(keyword in message_lower for keyword in weather_keywords):
            analysis["intent"] = "weather_inquiry"
            print(f"🌤️ MÉTÉO détectée avec: {[kw for kw in weather_keywords if kw in message_lower]}")
        
        # 2. Recommandations (mots-clés étendus)
        elif any(word in message_lower for word in [
            "recommand", "conseil", "suggestion", "propose", "idée", "inspir",
            "où aller", "où partir", "que visiter", "destination", "voyage",
            "recommande", "conseille", "suggère", "propose-moi", "aide-moi",
            "choix", "sélection", "option", "alternative", "préfère",
            "recommandations", "ia"
        ]):
            analysis["intent"] = "recommendation_request"
            print(f"🎯 RECOMMANDATION détectée")
        
        # 3. Budget
        elif analysis["entities"]["budget_indicators"]:
            analysis["intent"] = "budget_inquiry"
            print(f"💰 BUDGET détecté")
        
        # 4. Ville + activité spécifique
        elif analysis["entities"]["cities"] and analysis["entities"]["activities"]:
            analysis["intent"] = "specific_activity_city"
            print(f"🎯 ACTIVITÉ SPÉCIFIQUE détectée: {analysis['entities']['activities'][0]} à {analysis['entities']['cities'][0]}")
        
        # 5. Ville générale
        elif analysis["entities"]["cities"]:
            analysis["intent"] = "city_general"
            print(f"🗺️ VILLE GÉNÉRALE détectée: {analysis['entities']['cities'][0]}")
        
        # 6. Activité générale
        elif analysis["entities"]["activities"]:
            analysis["intent"] = "activity_general"
            print(f"🎪 ACTIVITÉ GÉNÉRALE détectée: {analysis['entities']['activities'][0]}")
        
        print(f"📊 Analyse finale - Intent: {analysis['intent']}, Villes: {analysis['entities']['cities']}, Activités: {analysis['entities']['activities']}")
        
        return analysis

    def _generate_smart_response(self, message_lower: str, analysis: Dict, user_id: str) -> str:
        """Génère une réponse intelligente basée sur l'analyse"""
        
        intent = analysis["intent"]
        entities = analysis["entities"]
        
        # Réponses selon l'intention détectée
        if intent == "weather_inquiry":
            return self._get_weather_response(entities.get("cities", ["paris"])[0] if entities.get("cities") else "paris")
        
        elif intent == "city_general":
            city = entities["cities"][0]
            return self._get_comprehensive_city_guide(city, message_lower)
        
        elif intent == "specific_activity_city":
            city = entities["cities"][0]
            activities = entities["activities"]
            return self._get_activity_specific_response(city, activities, message_lower)
        
        elif intent == "budget_inquiry":
            return self._get_budget_guide(entities.get("cities"))
        
        elif intent == "recommendation_request":
            return self._get_personalized_recommendations(user_id)
        
        else:
            # Réponse générale intelligente
            return self._get_contextual_general_response(message_lower, analysis)

    def _get_weather_response(self, city: str) -> str:
        """Génère une réponse météo complète"""
        if self.weather_service:
            try:
                weather_info = self.weather_service.get_current_weather(city)
                if weather_info:
                    advice = self.weather_service.get_travel_weather_advice(weather_info, ["général"])
                    
                    return f"""🌤️ **Météo Easy Travel - {city.title()}** ☀️

**🌡️ Conditions actuelles :**
• **Température** : {weather_info.temperature:.1f}°C (ressenti {weather_info.feels_like:.1f}°C)
• **Conditions** : {weather_info.description.title()}
• **Humidité** : {weather_info.humidity}%
• **Vent** : {weather_info.wind_speed:.1f} m/s
• **Visibilité** : {weather_info.visibility:.1f} km
• **Lever/Coucher** : {weather_info.sunrise} / {weather_info.sunset}

**👕 Conseils vestimentaires :**
{"• ❄️ Très froid - Manteau d'hiver indispensable" if weather_info.temperature < 5 else
"• 🧥 Frais - Veste chaude recommandée" if weather_info.temperature < 15 else  
"• 👕 Agréable - T-shirt + veste légère" if weather_info.temperature < 25 else
"• ☀️ Chaud - Vêtements légers et protection solaire"}

**💡 Conseils Easy Travel :**
{" • ".join(advice)}

*Météo temps réel pour optimiser votre voyage !* ✨"""
            except Exception as e:
                print(f"Erreur météo: {e}")
        
        return f"""🌤️ **Météo Easy Travel - {city.title()}** 📱

**🌡️ Conditions générales :**
• **Température moyenne** : 18-22°C
• **Conditions** : Variables selon la saison
• **Conseils** : Prévoir vêtements adaptables

**💡 Pour la météo temps réel :**
*Configurez OPENWEATHER_API_KEY pour des données précises*

**📅 Meilleures périodes pour {city.title()} :**
• 🌸 **Printemps** : Idéal pour visiter
• ☀️ **Été** : Chaud mais animé  
• 🍂 **Automne** : Parfait compromis
• ❄️ **Hiver** : Ambiance unique"""

    def _get_comprehensive_city_guide(self, city: str, message_lower: str) -> str:
        """Génère un guide complet de ville"""
        if city not in self.destinations_data:
            return self._get_destination_not_found_response(city)
        
        city_data = self.destinations_data[city]
        city_title = city.title()
        
        response = f"🌍 **{city_title} - Guide Easy Travel Complet** ✨\n\n"
        
        # Informations essentielles
        if "city_info" in city_data:
            info = city_data["city_info"]
            response += f"**📍 Informations essentielles :**\n"
            response += f"• 🏛️ Pays : {info.get('country', 'N/A')}\n"
            response += f"• 💰 Monnaie : {info.get('currency', 'N/A')}\n"
            response += f"• 🗣️ Langues : {', '.join(info.get('languages', []))}\n"
            response += f"• 💳 Pourboires : {info.get('tipping_culture', 'Standard')}\n"
            
            if 'emergency_numbers' in info:
                urgences = info['emergency_numbers']
                response += f"• 🚨 Urgences : {', '.join([f'{k} {v}' for k, v in list(urgences.items())[:2]])}\n"
            response += "\n"
        
        # Top attractions
        if "attractions" in city_data and city_data["attractions"]:
            response += f"**🎯 Top Attractions {city_title} :**\n"
            for i, attraction in enumerate(city_data["attractions"][:5], 1):
                name = attraction.get("name", "Attraction")
                category = attraction.get("category", "Site")
                rating = attraction.get("rating", "N/A")
                description = attraction.get("description", "")
                
                response += f"**{i}. {name}** ({category})\n"
                response += f"   ⭐ {rating}/5 | 📝 {description[:70]}...\n"
                
                # Informations pratiques
                price_level = attraction.get("price_level", 0)
                if price_level:
                    price_str = "€" * price_level
                    response += f"   💰 {price_str} | "
                
                duration = attraction.get("duration_visit", 0)
                if duration:
                    response += f"⏱️ {duration} min | "
                
                best_time = attraction.get("best_time_visit", "")
                if best_time:
                    response += f"🕐 {best_time}"
                
                response += "\n\n"
        
        # Restaurants authentiques
        if "restaurants" in city_data and city_data["restaurants"]:
            response += f"**🍽️ Restaurants Authentiques {city_title} :**\n"
            for i, restaurant in enumerate(city_data["restaurants"][:4], 1):
                name = restaurant.get("name", "Restaurant")
                cuisine = restaurant.get("cuisine_type", restaurant.get("cuisine", "Cuisine locale"))
                rating = restaurant.get("rating", "N/A")
                price_range = restaurant.get("price_range", "€€")
                specialties = restaurant.get("specialties", [])
                
                response += f"**{i}. {name}** ({cuisine})\n"
                response += f"   ⭐ {rating}/5 | 💰 {price_range}"
                
                if specialties:
                    response += f" | 🍴 {specialties[0]}"
                
                if restaurant.get("local_favorite"):
                    response += " | 🏆 Favori local"
                
                response += "\n"
            response += "\n"
        
        # Transport local
        if "transport" in city_data and city_data["transport"]:
            response += f"**🚇 Transport {city_title} :**\n"
            for transport in city_data["transport"][:3]:
                transport_type = transport.get("type", "Transport")
                cost = transport.get("cost", "N/A")
                description = transport.get("description", "")
                
                response += f"• **{transport_type}** - {cost}\n"
                if description:
                    response += f"  📝 {description[:60]}...\n"
                
                if "tips" in transport and transport["tips"]:
                    response += f"  💡 {transport['tips'][0]}\n"
            response += "\n"
        
        # Conseils pratiques et culturels
        if "city_info" in city_data:
            cultural_tips = city_data["city_info"].get("cultural_etiquette", [])
            safety_tips = city_data["city_info"].get("safety_tips", [])
            
            if cultural_tips or safety_tips:
                response += f"**💡 Conseils de Voyage :**\n"
                
                all_tips = (cultural_tips[:2] + safety_tips[:2])[:4]
                for tip in all_tips:
                    response += f"• {tip}\n"
                response += "\n"
        
        # Événements actuels
        if "events" in city_data and city_data["events"]:
            response += f"**🎭 Événements & Expériences :**\n"
            for event in city_data["events"][:2]:
                name = event.get("name", "Événement")
                description = event.get("description", "")
                date_info = event.get("start_date", event.get("date", ""))
                
                response += f"• **{name}**\n"
                if description:
                    response += f"  📝 {description[:60]}...\n"
                if date_info:
                    response += f"  📅 {date_info}\n"
            response += "\n"
        
        response += f"\n✨ *Guide authentique Easy Travel pour {city_title} !*"
        
        return response

    def _get_activity_specific_response(self, city: str, activities: List[str], message_lower: str) -> str:
        """Réponse spécialisée pour activité + ville"""
        if city not in self.destinations_data:
            return self._get_destination_not_found_response(city)
        
        city_data = self.destinations_data[city]
        city_title = city.title()
        main_activity = activities[0]
        
        response = f"🎯 **{main_activity.title()} à {city_title}** - Guide Spécialisé Easy Travel ✨\n\n"
        
        # Réponses spécialisées par activité
        if main_activity == "culture":
            # Attractions culturelles
            if "attractions" in city_data:
                cultural_attractions = [
                    attr for attr in city_data["attractions"] 
                    if any(keyword in attr.get("category", "").lower() 
                          for keyword in ["musée", "monument", "art", "culture", "historique"])
                ]
                
                if cultural_attractions:
                    response += f"**🏛️ Sites Culturels Incontournables :**\n"
                    for i, attr in enumerate(cultural_attractions[:4], 1):
                        response += f"{i}. **{attr['name']}** ({attr.get('category', 'Site')})\n"
                        response += f"   ⭐ {attr.get('rating', 'N/A')}/5 | 📍 {attr.get('description', '')[:50]}...\n"
                        
                        if attr.get("booking_required"):
                            response += f"   🎫 Réservation recommandée\n"
                        response += "\n"
        
        elif main_activity == "gastronomie":
            # Restaurants et spécialités
            if "restaurants" in city_data:
                response += f"**🍽️ Expérience Gastronomique {city_title} :**\n"
                for i, rest in enumerate(city_data["restaurants"][:4], 1):
                    response += f"{i}. **{rest['name']}** ({rest.get('cuisine_type', 'Cuisine locale')})\n"
                    response += f"   ⭐ {rest.get('rating', 'N/A')}/5 | 💰 {rest.get('price_range', '€€')}\n"
                    
                    specialties = rest.get("specialties", [])
                    if specialties:
                        response += f"   🍴 Spécialités : {', '.join(specialties[:2])}\n"
                    
                    if rest.get("local_favorite"):
                        response += f"   🏆 Authentique - Favori des locaux\n"
                    response += "\n"
        
        elif main_activity == "transport":
            # Informations transport détaillées
            if "transport" in city_data:
                response += f"**🚇 Guide Transport Complet {city_title} :**\n"
                for transport in city_data["transport"]:
                    response += f"**• {transport.get('type', 'Transport')}**\n"
                    response += f"  💰 {transport.get('cost', 'N/A')}\n"
                    response += f"  📝 {transport.get('description', '')}\n"
                    
                    if "tips" in transport:
                        response += f"  **💡 Conseils :**\n"
                        for tip in transport["tips"][:2]:
                            response += f"    - {tip}\n"
                    response += "\n"
        
        # Météo contextuelle pour l'activité
        if self.weather_service:
            try:
                weather = self.weather_service.get_current_weather(city)
                if weather:
                    weather_advice = self.weather_service.get_travel_weather_advice(weather, [main_activity])
                    if weather_advice:
                        response += f"**🌤️ Conditions Météo pour {main_activity.title()} :**\n"
                        response += f"• Température : {weather.temperature:.1f}°C - {weather.description}\n"
                        for advice in weather_advice[:2]:
                            response += f"• {advice}\n"
                        response += "\n"
            except:
                pass
        
        # Conseils spécialisés
        activity_tips = {
            "culture": [
                "Achetez un pass musées pour économiser",
                "Visitez tôt le matin pour éviter les foules",
                "Vérifiez les jours de gratuité"
            ],
            "gastronomie": [
                "Réservez les restaurants populaires à l'avance",
                "Déjeunez là où mangent les locaux",
                "Goûtez les spécialités de saison"
            ],
            "transport": [
                "Téléchargez les apps officielles",
                "Achetez les pass transport dès l'arrivée",
                "Gardez de la monnaie pour les distributeurs"
            ]
        }
        
        if main_activity in activity_tips:
            response += f"**💡 Conseils Pro {main_activity.title()} :**\n"
            for tip in activity_tips[main_activity]:
                response += f"• {tip}\n"
        
        response += f"\n✨ *Guide spécialisé Easy Travel pour {main_activity} à {city_title} !*"
        
        return response

    def _get_budget_guide(self, cities: Optional[List[str]] = None) -> str:
        """Guide budget personnalisé"""
        response = "💰 **Guide Budget Easy Travel** 📊\n\n"
        
        if cities:
            city = cities[0]
            city_title = city.title()
            response += f"**💰 Budget spécifique pour {city_title} :**\n\n"
            
            # Budget par ville selon les données
            budget_city_data = {
                "paris": {"low": "80-120€/jour", "medium": "120-200€/jour", "high": "200-400€/jour"},
                "rome": {"low": "60-100€/jour", "medium": "100-180€/jour", "high": "180-350€/jour"},
                "barcelone": {"low": "50-90€/jour", "medium": "90-160€/jour", "high": "160-300€/jour"},
                "lisbonne": {"low": "40-70€/jour", "medium": "70-130€/jour", "high": "130-250€/jour"},
                "singapour": {"low": "90-140€/jour", "medium": "140-250€/jour", "high": "250-500€/jour"},
                "tokyo": {"low": "100-150€/jour", "medium": "150-280€/jour", "high": "280-600€/jour"}
            }
            
            if city in budget_city_data:
                budgets = budget_city_data[city]
                response += f"**🎯 Fourchettes pour {city_title} :**\n"
                response += f"• 💸 **Économique** : {budgets['low']}\n"
                response += f"• 💼 **Confort** : {budgets['medium']}\n"
                response += f"• 🌟 **Premium** : {budgets['high']}\n\n"
        
        response += """**🎯 Répartition optimale :**
• 🏨 Hébergement : 40%
• 🍽️ Restauration : 30%  
• 🎫 Activités : 20%
• 🚇 Transport : 10%

**💡 Astuces d'économie :**
• Réservez 2 mois à l'avance (-25%)
• Déjeuner dans les marchés (-40%)
• Pass touristiques (-30%)
• Visites gratuites le dimanche

**🌟 Pro Tips Easy Travel :**
• Apps locales pour vraies bonnes affaires
• Évitez zones ultra-touristiques (-50%)
• Négociez dans les marchés
• Picnics = économies + découvertes"""

        return response

    def _get_personalized_recommendations(self, user_id: str) -> str:
        """Génère des recommandations personnalisées"""
        print(f"🎯 Génération recommandations pour user {user_id}")
        
        if not self.recommendation_engine:
            print("⚠️ Moteur de recommandations non disponible, fallback")
            return self._get_general_recommendations()
        
        # Analyse des préférences utilisateur depuis l'historique
        user_preferences = self._analyze_user_preferences(user_id)
        print(f"📊 Préférences détectées: {user_preferences}")
        
        try:
            recommendations = self.recommendation_engine.get_personalized_recommendations(user_preferences)
            print(f"✅ {len(recommendations)} recommandations générées")
            
            response = "🎯 **Recommandations Personnalisées Easy Travel** ✨\n\n"
            
            if recommendations:
                response += "**🌍 Destinations parfaites pour vous :**\n\n"
                
                for i, rec in enumerate(recommendations[:4], 1):  # Augmenté à 4
                    response += f"**{i}. {rec['destination']}** ({rec['region'].title()})\n"
                    response += f"   🎯 Compatibilité : {int(rec['score']*100)}%\n"
                    response += f"   💡 Parfait car : {rec['reason']}\n"
                    response += f"   💰 Budget estimé : {rec['estimated_budget']}\n"
                    response += f"   🎪 Activités : {', '.join(rec['best_activities'][:3])}\n"
                    
                    if rec.get('best_months'):
                        response += f"   📅 Idéal : {', '.join(rec['best_months'][:3])}\n"
                    
                    response += "\n"
                
                # Conseils personnalisés basés sur l'historique
                if user_preferences.get("conversation_count", 0) > 0:
                    response += "**💡 Conseils personnalisés :**\n"
                    
                    if user_preferences.get("budget_range") == "low":
                        response += "• Focus sur destinations économiques\n"
                    elif user_preferences.get("budget_range") == "high":
                        response += "• Expériences premium disponibles\n"
                    
                    if user_preferences.get("preferred_activities"):
                        activities = user_preferences["preferred_activities"][:2]
                        response += f"• Spécialisé {'/'.join(activities)} selon vos goûts\n"
                    
                    response += "• Basé sur notre conversation précédente\n"
                    response += "• Plus vous me parlez, mieux je vous conseille !\n\n"
                
                response += "**🚀 Prêt(e) à partir ?**\n"
                response += "Demandez-moi des détails sur une destination qui vous intéresse !\n\n"
                response += "✨ *Recommandations IA générées spécialement pour vous !*"
            else:
                print("⚠️ Aucune recommandation générée, fallback")
                response += self._get_general_recommendations()
                
        except Exception as e:
            print(f"❌ Erreur recommandations: {e}")
            response = "🎯 **Recommandations Easy Travel** ✨\n\n"
            response += self._get_general_recommendations()
        
        return response

    def _analyze_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Analyse les préférences utilisateur depuis l'historique"""
        preferences = {
            "preferred_activities": [],
            "budget_range": "medium",
            "preferred_climate": None,
            "conversation_count": 0
        }
        
        if user_id in self.conversation_history:
            messages = self.conversation_history[user_id]
            preferences["conversation_count"] = len([m for m in messages if m["type"] == "user"])
            
            # Analyse des activités mentionnées
            all_text = " ".join([m["message"].lower() for m in messages if m["type"] == "user"])
            
            activity_mentions = {
                "culture": ["musée", "monument", "art", "histoire", "culture"],
                "gastronomie": ["restaurant", "cuisine", "manger", "food"],
                "nature": ["nature", "plage", "montagne", "parc"],
                "shopping": ["shopping", "boutique", "achats"],
                "nightlife": ["bar", "sortie", "nuit"]
            }
            
            for activity, keywords in activity_mentions.items():
                if any(keyword in all_text for keyword in keywords):
                    preferences["preferred_activities"].append(activity)
            
            # Analyse du budget
            if any(word in all_text for word in ["luxe", "premium", "cher"]):
                preferences["budget_range"] = "high"
            elif any(word in all_text for word in ["économique", "budget", "pas cher"]):
                preferences["budget_range"] = "low"
        
        return preferences

    def _get_general_recommendations(self) -> str:
        """Recommandations générales si le moteur n'est pas disponible"""
        cities = list(self.destinations_data.keys())[:4]
        
        response = "🎯 **Recommandations Easy Travel** ✨\n\n"
        response += "**🌍 Destinations populaires :**\n\n"
        
        for i, city in enumerate(cities, 1):
            city_title = city.title()
            city_data = self.destinations_data[city]
            
            response += f"**{i}. {city_title}**\n"
            
            if "city_info" in city_data:
                country = city_data["city_info"].get("country", "")
                response += f"   🏛️ {country}\n"
            
            if "attractions" in city_data:
                attraction_count = len(city_data["attractions"])
                response += f"   🎯 {attraction_count} attractions\n"
            
            if "restaurants" in city_data:
                restaurant_count = len(city_data["restaurants"])
                response += f"   🍽️ {restaurant_count} restaurants\n"
            
            response += "\n"
        
        response += "**💡 Pour des recommandations personnalisées :**\n"
        response += "• Parlez-moi de vos goûts\n"
        response += "• Mentionnez votre budget\n"
        response += "• Décrivez vos activités préférées\n\n"
        response += "✨ *Je m'adapterai à vos préférences !*"
        
        return response

    def _get_contextual_general_response(self, message_lower: str, analysis: Dict) -> str:
        """Réponse générale contextuelle"""
        if any(word in message_lower for word in ["bonjour", "salut", "hello", "bonsoir"]):
            return self._get_welcome_message()
        elif any(word in message_lower for word in ["aide", "help", "comment", "que faire"]):
            return self._get_help_message()
        elif any(word in message_lower for word in ["merci", "thanks"]):
            return "🙏 **De rien !** Je suis là pour vous aider à planifier le voyage parfait ! N'hésitez pas si vous avez d'autres questions. ✨"
        
        # NOUVEAU: Détection étendue de demandes de recommandations
        elif any(word in message_lower for word in [
            "où", "quoi", "que", "partir", "aller", "visiter", "voyage", "destination",
            "idée", "inspiration", "choix", "sélection", "option"
        ]):
            print("🎯 Détection recommandation dans contextuel")
            return self._get_personalized_recommendations("default")
        
        else:
            return self._get_smart_general_response(message_lower)

    def _get_welcome_message(self) -> str:
        """Message de bienvenue personnalisé"""
        cities_list = ", ".join([city.title() for city in list(self.destinations_data.keys())[:6]])
        
        return f"""✈️ **Bienvenue sur Easy Travel !** 🌍

Je suis votre assistant voyage **avec données authentiques** ! 🤖

**🚀 Mes capacités avancées :**
• 🗺️ **Données réelles** - Issues de vos fichiers JSON
• 🌤️ **Météo temps réel** - Conditions actuelles
• 🎯 **Recommandations IA** - Personnalisées pour vous
• 💰 **Conseils budget** - Optimisation garantie
• 🏨 **Hébergements** - Toutes gammes
• 🍽️ **Gastronomie locale** - Vraies recommandations

**🌍 Vos destinations disponibles :**
{cities_list}{"..." if len(self.destinations_data) > 6 else ""}

**✨ Exemples intelligents :**
• *"Météo à Paris"*
• *"Restaurants à {list(self.destinations_data.keys())[0].title()}"*  
• *"Recommandations pour moi"*
• *"Budget pour {list(self.destinations_data.keys())[1].title() if len(self.destinations_data) > 1 else 'Rome'}"*

**🎯 IA adaptative + Données authentiques !**
**🚀 Où voulez-vous voyager ?**"""

    def _get_help_message(self) -> str:
        """Message d'aide"""
        return """🤖 **Guide d'utilisation Easy Travel** 📚

**🎯 Ce que je peux faire pour vous :**

**🌍 Informations destinations :**
• *"Guide complet de Paris"*
• *"Attractions à Rome"*
• *"Restaurants à Barcelone"*

**🌤️ Météo temps réel :**
• *"Météo à Tokyo"*
• *"Temps qu'il fait à Lisbonne"*

**💰 Conseils budget :**
• *"Budget pour Singapour"*
• *"Combien coûte un voyage à Paris ?"*

**🎯 Recommandations IA :**
• *"Recommande-moi une destination"*
• *"Où partir selon mes goûts ?"*

**🚇 Transport et pratique :**
• *"Comment se déplacer à Rome ?"*
• *"Transport public Paris"*

**💡 Conseils :**
• Soyez spécifique dans vos questions
• Mentionnez vos préférences (budget, activités)
• Je m'adapte à votre style de voyage !

**✨ Plus vous me parlez, mieux je vous conseille !**"""

    def _get_smart_general_response(self, message_lower: str) -> str:
        """Réponse générale intelligente"""
        
        # Cas spéciaux de demandes implicites de recommandations
        if any(pattern in message_lower for pattern in [
            "pas d'idée", "sais pas", "hésite", "indécis", "pas sûr",
            "aucune idée", "me décider", "choisir", "hésitation"
        ]):
            print("🎯 Demande implicite de recommandation détectée")
            return self._get_personalized_recommendations("default")
        
        return """🤔 **Je peux vous aider !** 

**💡 Essayez plutôt :**
• *"Recommande-moi une destination"* pour suggestions IA
• *"Guide de [ville]"* pour infos complètes
• *"Météo à [ville]"* pour conditions actuelles  
• *"Restaurants à [ville]"* pour gastronomie
• *"Budget [ville]"* pour conseils financiers

**🌍 Villes disponibles :**""" + f"""
{', '.join([city.title() for city in list(self.destinations_data.keys())[:8]])}

**🎯 Ou dites-moi simplement "où partir ?" pour des recommandations !**"""

    def _get_destination_not_found_response(self, city: str) -> str:
        """Réponse quand une destination n'est pas trouvée"""
        available_cities = list(self.destinations_data.keys())
        similar_cities = [c for c in available_cities if city[:3] in c or c[:3] in city]
        
        response = f"😔 **Désolé, je n'ai pas d'informations sur {city.title()}**\n\n"
        
        if similar_cities:
            response += f"**🤔 Cherchiez-vous plutôt :**\n"
            for similar in similar_cities[:3]:
                response += f"• {similar.title()}\n"
            response += "\n"
        
        response += f"**🌍 Destinations disponibles :**\n"
        for city_name in available_cities[:6]:
            response += f"• {city_name.title()}\n"
        
        response += f"\n**💡 Demandez simplement :**\n"
        response += f"*\"Guide de {available_cities[0].title()}\"*\n\n"
        response += "✨ *J'ajoute régulièrement de nouvelles destinations !*"
        
        return response

    def _generate_smart_suggestions(self, message_lower: str, analysis: Dict) -> List[str]:
        """Génère des suggestions intelligentes"""
        suggestions = []
        
        print(f"🎯 Génération suggestions pour intent: {analysis['intent']}")
        
        # Suggestions basées sur l'intention détectée
        if analysis["intent"] == "weather_inquiry":
            city = analysis["entities"]["cities"][0] if analysis["entities"]["cities"] else "paris"
            suggestions = [
                f"🌤️ Prévisions {city.title()}",
                f"👕 Conseils vêtements {city.title()}",
                f"📅 Meilleure période {city.title()}",
                f"🗺️ Guide {city.title()}"
            ]
            print(f"🌤️ Suggestions météo générées pour {city}")
            
        elif analysis["intent"] == "city_general":
            city = analysis["entities"]["cities"][0] if analysis["entities"]["cities"] else "paris"
            suggestions = [
                f"🍽️ Restaurants {city.title()}",
                f"🚇 Transport {city.title()}",
                f"🌤️ Météo {city.title()}",
                f"💰 Budget {city.title()}"
            ]
            print(f"🗺️ Suggestions ville générées pour {city}")
            
        elif analysis["intent"] == "specific_activity_city":
            city = analysis["entities"]["cities"][0] if analysis["entities"]["cities"] else "paris"
            activity = analysis["entities"]["activities"][0] if analysis["entities"]["activities"] else "culture"
            suggestions = [
                f"🎯 Plus sur {activity} {city.title()}",
                f"🌤️ Météo {city.title()}",
                f"💰 Budget {activity} {city.title()}",
                f"🗺️ Guide complet {city.title()}"
            ]
            print(f"🎪 Suggestions activité générées pour {activity} à {city}")
            
        elif analysis["intent"] == "budget_inquiry":
            suggestions = ["💡 Astuces économies", "🏨 Hébergements budget", "🎫 Pass touristiques", "🍽️ Restaurants abordables"]
            print(f"💰 Suggestions budget générées")
            
        elif analysis["intent"] == "recommendation_request":
            suggestions = ["🌍 Plus de recommandations", "💰 Budget personnalisé", "📅 Planifier voyage", "🎯 Affiner préférences"]
            print(f"🎯 Suggestions recommandations générées")
            
        else:
            # Suggestions générales basées sur les données disponibles
            available_cities = list(self.destinations_data.keys())
            if len(available_cities) >= 2:
                suggestions = [
                    f"🗺️ Guide {available_cities[0].title()}",
                    f"🍽️ Restaurants {available_cities[1].title()}",
                    "🎯 Recommandations IA",
                    "🌤️ Météo temps réel"
                ]
            else:
                suggestions = ["🗺️ Planifier voyage", "💰 Budget voyage", "🌤️ Météo destination", "🍽️ Gastronomie locale"]
            print(f"📝 Suggestions générales générées")
        
        print(f"✅ {len(suggestions)} suggestions finales: {suggestions}")
        return suggestions

    def _extract_user_preferences(self, message: str, user_id: str) -> Dict[str, Any]:
        """Extrait les préférences utilisateur du message"""
        preferences = {}
        message_lower = message.lower()
        
        # Détection budget
        if any(word in message_lower for word in ["économique", "pas cher", "budget serré"]):
            preferences["budget_preference"] = "low"
        elif any(word in message_lower for word in ["luxe", "premium", "haut de gamme"]):
            preferences["budget_preference"] = "high"
        elif any(word in message_lower for word in ["moyen", "raisonnable", "standard"]):
            preferences["budget_preference"] = "medium"
        
        # Détection style de voyage
        if any(word in message_lower for word in ["famille", "enfants", "kids"]):
            preferences["travel_style"] = "family"
        elif any(word in message_lower for word in ["romantique", "couple", "amoureux"]):
            preferences["travel_style"] = "romantic"
        elif any(word in message_lower for word in ["aventure", "sport", "extrême"]):
            preferences["travel_style"] = "adventure"
        
        return preferences

    def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Récupère le profil utilisateur"""
        if user_id not in self.conversation_history:
            return {}
        
        messages = self.conversation_history[user_id]
        user_messages = [m for m in messages if m["type"] == "user"]
        
        # Analyse des préférences depuis l'historique
        preferences = self._analyze_user_preferences(user_id)
        
        return {
            "conversation_count": len(user_messages),
            "last_interaction": messages[-1]["timestamp"] if messages else None,
            "preferences": preferences,
            "engagement_level": "high" if len(user_messages) > 5 else "medium" if len(user_messages) > 2 else "new"
        }

# === SERVEUR HTTP ===
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
        weather_status = "✅ Actif" if chatbot.weather_service else "⚠️ Mode fallback"
        recommendation_status = "✅ Actif" if chatbot.recommendation_engine else "⚠️ Mode fallback"
        
        info = {
            "service": "Easy Travel API Complet",
            "version": "2.0.0 - Tous services intégrés",
            "python_version": f"{sys.version.split()[0]}",
            "status": "🚀 Opérationnel",
            "services": {
                "weather_service": weather_status,
                "recommendation_engine": recommendation_status,
                "local_data": "✅ Chargé",
                "ai_analysis": "✅ Actif"
            },
            "data_source": "Fichiers JSON authentiques + APIs",
            "destinations_loaded": len(chatbot.destinations_data),
            "destinations_available": list(chatbot.destinations_data.keys()),
            "endpoints": {
                "chat": "POST /api/chat",
                "health": "GET /api/health",
                "destinations": "GET /api/destinations",
                "debug": "GET /api/debug"
            },
            "features": [
                "🌤️ Météo temps réel",
                "🎯 Recommandations IA",
                "💰 Conseils budget",
                "🗺️ Guides complets",
                "📱 Compatible mobile"
            ],
            "test_example": 'curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d \'{"message":"Météo à Paris"}\''
        }
        self.send_json_response(info)
    
    def send_health_check(self):
        """Health check de l'API"""
        health = {
            "status": "healthy",
            "mode": "full_services",
            "python_version": f"{sys.version.split()[0]}",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "weather": bool(chatbot.weather_service),
                "recommendations": bool(chatbot.recommendation_engine),
                "local_data": len(chatbot.destinations_data) > 0
            },
            "destinations_count": len(chatbot.destinations_data),
            "active_conversations": len(chatbot.conversation_history),
            "data_source": "Fichiers JSON + APIs externes",
            "memory_usage": "Optimisé"
        }
        self.send_json_response(health)
    
    def send_destinations(self):
        """Liste des destinations avec statistiques complètes"""
        destinations_info = {}
        for city, data in chatbot.destinations_data.items():
            city_title = city.title()
            destinations_info[city_title] = {
                "attractions_count": len(data.get("attractions", [])),
                "restaurants_count": len(data.get("restaurants", [])),
                "has_transport_info": "transport" in data,
                "has_events": "events" in data,
                "has_city_info": "city_info" in data,
                "weather_available": bool(chatbot.weather_service),
                "ai_recommendations": bool(chatbot.recommendation_engine)
            }
        
        result = {
            "destinations": list(destinations_info.keys()),
            "count": len(destinations_info),
            "details": destinations_info,
            "services_status": {
                "weather": "✅ Disponible" if chatbot.weather_service else "❌ Non configuré",
                "recommendations": "✅ Actif" if chatbot.recommendation_engine else "❌ Non disponible"
            },
            "status": "success",
            "data_source": "Fichiers JSON authentiques + Services externes"
        }
        self.send_json_response(result)
    
    def send_debug_info(self):
        """Informations de debug complètes"""
        debug_info = {
            "system": {
                "python_version": sys.version.split()[0],
                "server_time": datetime.now().isoformat(),
                "destinations_loaded": len(chatbot.destinations_data)
            },
            "services": {
                "weather_service": {
                    "available": bool(chatbot.weather_service),
                    "api_key_configured": bool(os.getenv("OPENWEATHER_API_KEY"))
                },
                "recommendation_engine": {
                    "available": bool(chatbot.recommendation_engine),
                    "destinations_db_size": len(chatbot.recommendation_engine.destinations_db) if chatbot.recommendation_engine else 0
                }
            },
            "data_analysis": {}
        }
        
        # Analyse de la structure des données
        for city, data in list(chatbot.destinations_data.items())[:3]:  # 3 premiers
            debug_info["data_analysis"][city] = {
                "main_keys": list(data.keys()),
                "attractions": {
                    "count": len(data.get("attractions", [])),
                    "sample": data.get("attractions", [{}])[0].get("name", "N/A") if data.get("attractions") else "N/A"
                },
                "restaurants": {
                    "count": len(data.get("restaurants", [])),
                    "sample": data.get("restaurants", [{}])[0].get("name", "N/A") if data.get("restaurants") else "N/A"
                },
                "city_info_complete": "city_info" in data and bool(data["city_info"])
            }
        
        self.send_json_response(debug_info)
    
    def handle_chat(self):
        """Gestionnaire du chat avec tous les services"""
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
            
            # Traitement avec tous les services intégrés
            print(f"💬 Message reçu: {message[:50]}...")
            response = chatbot.process_message(message, user_id)
            print(f"✅ Réponse générée avec IA ({len(response['message'])} caractères)")
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"❌ Erreur chat: {e}")
            self.send_json_response({
                "message": f"😔 **Erreur serveur Easy Travel**\n\nErreur: {str(e)}\n\nTous les services sont chargés mais une erreur de traitement s'est produite.",
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

# Instance globale du chatbot avec tous les services
chatbot = EasyTravelChatbot()

def run_server(port=8000):
    """Lance le serveur HTTP avec tous les services"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, EasyTravelHandler)
    
    print(f"\n🚀 Easy Travel Server COMPLET - Tous services intégrés !")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🤖 Chatbot: IA avancée + Données authentiques")
    print(f"🗺️ Destinations chargées: {len(chatbot.destinations_data)}")
    print(f"📁 Vos villes: {', '.join([city.title() for city in chatbot.destinations_data.keys()])}")
    
    print(f"\n🔧 Services disponibles:")
    print(f"   🌤️ Météo: {'✅ Actif (API)' if chatbot.weather_service else '⚠️ Mode fallback'}")
    print(f"   🎯 Recommandations: {'✅ IA active' if chatbot.recommendation_engine else '⚠️ Mode général'}")
    print(f"   📊 Données locales: ✅ {len(chatbot.destinations_data)} villes")
    print(f"   🧠 Analyse IA: ✅ Contextuelle")
    
    print(f"\n🔥 API Endpoints:")
    print(f"   GET  http://localhost:{port}/")
    print(f"   POST http://localhost:{port}/api/chat")
    print(f"   GET  http://localhost:{port}/api/destinations")
    print(f"   GET  http://localhost:{port}/api/health")
    print(f"   GET  http://localhost:{port}/api/debug")
    
    print(f"\n💡 Tests avec services complets:")
    print(f'   Météo:  curl -X POST http://localhost:{port}/api/chat -d \'{{"message":"Météo à Paris"}}\'')
    print(f'   Guide:  curl -X POST http://localhost:{port}/api/chat -d \'{{"message":"Guide Rome"}}\'')
    print(f'   IA:     curl -X POST http://localhost:{port}/api/chat -d \'{{"message":"Recommandations pour moi"}}\'')
    
    print(f"\n⚙️ Configuration optionnelle:")
    if not os.getenv("OPENWEATHER_API_KEY"):
        print(f"   🌤️ OPENWEATHER_API_KEY non configuré (mode fallback)")
    else:
        print(f"   🌤️ OPENWEATHER_API_KEY configuré ✅")
    
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print(f"   🗺️ GOOGLE_MAPS_API_KEY non configuré (optionnel)")
    else:
        print(f"   🗺️ GOOGLE_MAPS_API_KEY configuré ✅")
    
    print(f"\n🛑 Arrêt: Ctrl+C")
    print(f"="*80)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur Easy Travel...")
        httpd.shutdown()

if __name__ == "__main__":
    # Vérification des dépendances optionnelles
    try:
        import requests
        print("✅ Module 'requests' disponible")
    except ImportError:
        print("⚠️ Module 'requests' non installé - fonctionnalités limitées")
        print("   Installez avec: pip install requests")
    
    print(f"\n🎯 Configuration détectée:")
    print(f"   📁 Dossier de données: {len(chatbot.destinations_data)} villes chargées")
    print(f"   🌤️ Service météo: {'✅' if WEATHER_SERVICE_AVAILABLE else '❌'}")
    print(f"   🎯 Recommandations: {'✅' if RECOMMENDATION_ENGINE_AVAILABLE else '❌'}")
    
    run_server()