from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from .prompts import EASY_TRAVEL_PROMPT
from services.database import UserDatabase
from services.travel_api import TravelAPI
from services.recommendation import TravelRecommendationEngine
from services.local_data_service import LocalDataService
from services.weather_service import WeatherService
from services.interactive_journey import InteractiveJourneyOrchestrator
from models.user_profile import UserProfile, UserPreferences, TravelPlan
from utils.helpers import TravelHelpers

load_dotenv()

# Configuration proxy plus sûre - désactivée temporairement pour éviter les conflits
# Les proxies seront gérés individuellement si nécessaire
# if os.getenv("HTTP_PROXY"):
#     os.environ["HTTP_PROXY"] = os.getenv("HTTP_PROXY")
# if os.getenv("HTTPS_PROXY"):
#     os.environ["HTTPS_PROXY"] = os.getenv("HTTPS_PROXY")


def apply_httpx_fix():
    """Applique le fix pour le problème d'argument 'proxies' avec httpx/OpenAI"""
    try:
        import httpx

        # Fix pour httpx.Client (synchrone)
        if not hasattr(httpx.Client, "_original_init"):
            httpx.Client._original_init = httpx.Client.__init__

            def fixed_init(self, *args, **kwargs):
                kwargs.pop("proxies", None)
                return self._original_init(*args, **kwargs)

            httpx.Client.__init__ = fixed_init

        # Fix pour httpx.AsyncClient (asynchrone) - SOLUTION CRITIQUE
        if not hasattr(httpx.AsyncClient, "_original_init"):
            httpx.AsyncClient._original_init = httpx.AsyncClient.__init__

            def fixed_async_init(self, *args, **kwargs):
                kwargs.pop("proxies", None)
                return self._original_init(*args, **kwargs)

            httpx.AsyncClient.__init__ = fixed_async_init

        print("✅ Fix httpx Client + AsyncClient appliqué avec succès")
        return True

    except Exception as e:
        print(f"⚠️ Impossible d'appliquer le fix httpx: {e}")
        return False


def create_chat_openai_safely():
    """Crée une instance ChatOpenAI avec gestion d'erreur robuste"""
    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key or openai_key == "your_openai_key_here":
        print("⚠️  OPENAI_API_KEY non configurée - mode démo")
        return None

    # Nettoyage complet de l'environnement proxy
    proxy_vars = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
    ]
    saved_proxies = {}

    # Sauvegarde et supprime tous les proxies
    for var in proxy_vars:
        if var in os.environ:
            saved_proxies[var] = os.environ[var]
            del os.environ[var]

    # SOLUTION FINALE: Applique le fix httpx avant toute initialisation
    apply_httpx_fix()

    try:
        import importlib
        import sys

        # Supprime les modules mis en cache qui pourraient avoir des proxies
        modules_to_reload = [
            mod
            for mod in sys.modules.keys()
            if any(x in mod for x in ["httpx", "openai", "langchain_openai"])
        ]

        # Essaie plusieurs configurations ultra-basiques
        configs_to_try = [
            # Configuration minimale absolue
            {
                "model": "gpt-3.5-turbo",
                "openai_api_key": openai_key,
            },
            # Avec température
            {
                "model": "gpt-3.5-turbo",
                "openai_api_key": openai_key,
                "temperature": 0.7,
            },
        ]

        for i, config in enumerate(configs_to_try):
            try:
                llm = ChatOpenAI(**config)
                print(f"✅ ChatOpenAI initialisé (config {i+1})")
                return llm
            except Exception as e:
                print(f"❌ Échec config {i+1}: {e}")
                continue

    finally:
        # Restaure les proxies
        for var, value in saved_proxies.items():
            os.environ[var] = value

    print("❌ Impossible d'initialiser ChatOpenAI")
    return None

    print("❌ Impossible d'initialiser ChatOpenAI")
    return None


def create_direct_openai_client():
    """Alternative: crée un client OpenAI direct si LangChain échoue"""
    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key or openai_key == "your_openai_key_here":
        return None

    # Nettoyage complet des proxies pour OpenAI direct
    proxy_vars = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
    ]
    saved_proxies = {}

    # Sauvegarde et supprime tous les proxies
    for var in proxy_vars:
        if var in os.environ:
            saved_proxies[var] = os.environ[var]
            del os.environ[var]

    # SOLUTION FINALE: Applique le fix httpx avant création du client
    apply_httpx_fix()

    try:
        import openai

        # Configuration ultra-simple sans proxy
        client = openai.OpenAI(
            api_key=openai_key,
            # Pas de configuration proxy du tout
        )

        # Test rapide
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5,
        )

        print("✅ Client OpenAI direct créé et testé")
        return client

    except Exception as e:
        print(f"❌ Erreur client OpenAI direct: {e}")
        return None
    finally:
        # Restaure les proxies
        for var, value in saved_proxies.items():
            os.environ[var] = value


class EasyTravelChatbot:
    def __init__(self):
        # Configuration plus robuste de ChatOpenAI
        self.llm = create_chat_openai_safely()
        self.direct_openai_client = None

        if not self.llm:
            print("⚠️  LangChain ChatOpenAI échec, essai client direct...")
            # Essaie un client OpenAI direct en fallback
            self.direct_openai_client = create_direct_openai_client()

            if self.direct_openai_client:
                print("✅ Client OpenAI direct disponible")
                self.llm = None  # Pas de LangChain LLM
                self.conversation = None
            else:
                print("⚠️  Mode dégradé: aucun LLM disponible")
                self.llm = None
                self.conversation = None
        else:
            # Initialisation normale avec LLM
            self.memory = ConversationBufferWindowMemory(
                k=10, return_messages=True  # Garde les 10 derniers échanges
            )

            self.prompt = PromptTemplate(
                input_variables=["history", "input"], template=EASY_TRAVEL_PROMPT
            )

            self.conversation = ConversationChain(
                llm=self.llm, memory=self.memory, prompt=self.prompt, verbose=True
            )

        self.db = UserDatabase()
        self.travel_api = TravelAPI()
        self.recommendation_engine = TravelRecommendationEngine()

        # Nouveaux services enrichis
        self.local_data_service = LocalDataService()
        self.weather_service = WeatherService()
        self.journey_orchestrator = InteractiveJourneyOrchestrator()

        self.user_preferences = {}
        self.current_user_profile = None

    def process_message(self, user_input: str, user_id: str = None) -> str:
        """Traite un message utilisateur et retourne la réponse du chatbot"""

        # Charge ou crée le profil utilisateur
        if user_id:
            self.current_user_profile = self.db.get_user_profile_model(user_id)
            if not self.current_user_profile:
                # Crée un nouveau profil
                self.current_user_profile = UserProfile(user_id=user_id)
                self.db.create_or_update_user_profile(self.current_user_profile)

            self.user_preferences = self.current_user_profile.preferences.dict()

        # Analyse et extraction avancée des préférences
        new_preferences = self._extract_preferences_advanced(user_input)
        self.user_preferences.update(new_preferences)

        # Met à jour le profil utilisateur
        if user_id and new_preferences:
            self._update_user_profile(new_preferences)

        # Contexte enrichi avec recommandations intelligentes
        enriched_input = self._enrich_context_advanced(user_input)

        # Génère la réponse via LangChain, client direct, ou mode dégradé
        if self.conversation:
            # Mode LangChain normal
            response = self.conversation.predict(input=enriched_input)
        elif self.direct_openai_client:
            # Mode client OpenAI direct
            response = self._generate_direct_openai_response(enriched_input)
        else:
            # Mode dégradé - réponse basique avec les services locaux
            response = self._generate_fallback_response(user_input, enriched_input)

        # Sauvegarde la conversation
        if user_id:
            self._save_interaction(user_id, user_input, response)

        return response

    def _extract_preferences_advanced(self, user_input: str) -> dict:
        """Extrait les préférences de voyage du message utilisateur avec les helpers"""
        preferences = {}

        # Utilise les helpers pour une extraction plus sophistiquée
        budget = TravelHelpers.extract_budget_from_text(user_input)
        if budget:
            preferences["budget"] = budget
            preferences["budget_range"] = TravelHelpers.categorize_budget(budget)

        destinations = TravelHelpers.extract_destinations_from_text(user_input)
        if destinations:
            preferences["preferred_destinations"] = destinations
            preferences["destination"] = destinations[
                0
            ]  # Première destination mentionnée

        date_info = TravelHelpers.extract_dates_from_text(user_input)
        if date_info:
            preferences.update(date_info)

        activities = TravelHelpers.extract_activities_from_text(user_input)
        if activities:
            preferences["preferred_activities"] = activities

        travel_type = TravelHelpers.determine_travel_type(user_input, activities)
        if travel_type:
            preferences["travel_type"] = travel_type.value

        return preferences

    def _update_user_profile(self, new_preferences: dict):
        """Met à jour le profil utilisateur avec les nouvelles préférences"""
        if not self.current_user_profile:
            return

        # Met à jour les préférences du profil
        current_prefs = self.current_user_profile.preferences

        if "budget_range" in new_preferences:
            current_prefs.budget_range = new_preferences["budget_range"]

        if "preferred_destinations" in new_preferences:
            # Ajoute sans doublons
            existing = set(current_prefs.preferred_destinations)
            new_dests = set(new_preferences["preferred_destinations"])
            current_prefs.preferred_destinations = list(existing.union(new_dests))

        if "preferred_activities" in new_preferences:
            existing = set(current_prefs.preferred_activities)
            new_activities = set(new_preferences["preferred_activities"])
            current_prefs.preferred_activities = list(existing.union(new_activities))

        if "travel_type" in new_preferences:
            current_prefs.travel_type = new_preferences["travel_type"]

        # Met à jour l'activité
        self.current_user_profile.update_activity()

        # Sauvegarde en base
        self.db.create_or_update_user_profile(self.current_user_profile)

    def _enrich_context_advanced(self, user_input: str) -> str:
        """Enrichit le contexte avec des données locales, météo et recommandations intelligentes"""
        context_parts = [user_input]

        # Si une destination est mentionnée, enrichir avec des données locales
        destinations = TravelHelpers.extract_destinations_from_text(user_input)
        if destinations:
            main_destination = destinations[0]

            # Informations météo
            try:
                weather = self.weather_service.get_current_weather(main_destination)
                if weather:
                    weather_context = f"\n[CONTEXTE MÉTÉO pour {main_destination}]: Température: {weather.temperature}°C, {weather.description}, Humidité: {weather.humidity}%"
                    context_parts.append(weather_context)

                    # Conseils météo selon les activités
                    activities = TravelHelpers.extract_activities_from_text(user_input)
                    if activities:
                        weather_advice = self.weather_service.get_travel_weather_advice(
                            weather, activities
                        )
                        if weather_advice:
                            context_parts.append(
                                f"\n[CONSEILS MÉTÉO]: {'; '.join(weather_advice)}"
                            )
            except Exception as e:
                print(f"Erreur météo: {e}")

            # Données locales enrichies
            try:
                # Informations générales sur la ville
                city_info = self.local_data_service.get_city_info(main_destination)
                if city_info:
                    local_context = f"\n[INFOS LOCALES {main_destination}]: Monnaie: {city_info.currency}, Langues: {', '.join(city_info.languages[:2])}"
                    context_parts.append(local_context)

                # Attractions recommandées
                attractions = self.local_data_service.get_local_attractions(
                    main_destination
                )
                if attractions:
                    top_attractions = attractions[:3]  # Top 3
                    attractions_text = ", ".join(
                        [f"{a.name} ({a.category})" for a in top_attractions]
                    )
                    context_parts.append(f"\n[ATTRACTIONS LOCALES]: {attractions_text}")

                # Restaurants locaux
                restaurants = self.local_data_service.get_local_restaurants(
                    main_destination
                )
                if restaurants:
                    top_restaurants = restaurants[:2]  # Top 2
                    restaurants_text = ", ".join(
                        [f"{r.name} ({r.cuisine_type})" for r in top_restaurants]
                    )
                    context_parts.append(f"\n[RESTAURANTS LOCAUX]: {restaurants_text}")

            except Exception as e:
                print(f"Erreur données locales: {e}")

        # Recommandations personnalisées basées sur le profil utilisateur
        if self.current_user_profile:
            try:
                recommendations = (
                    self.recommendation_engine.get_personalized_recommendations(
                        self.current_user_profile, limit=3
                    )
                )
                if recommendations:
                    rec_text = ", ".join(
                        [rec["destination"] for rec in recommendations]
                    )
                    context_parts.append(
                        f"\n[RECOMMANDATIONS PERSONNALISÉES]: {rec_text}"
                    )
            except Exception as e:
                print(f"Erreur recommandations: {e}")

        return "\n".join(context_parts)

        # Ajoute les préférences actuelles
        if self.user_preferences:
            formatted_prefs = TravelHelpers.format_preferences_for_display(
                self.user_preferences
            )
            context_parts.append(
                f"\nPréférences utilisateur actuelles:\n{formatted_prefs}"
            )

        # Ajoute des recommandations personnalisées
        if self.current_user_profile:
            recommendations = (
                self.recommendation_engine.get_personalized_recommendations(
                    self.current_user_profile, limit=3
                )
            )

            if recommendations:
                rec_text = "\nRecommandations personnalisées:\n"
                for i, rec in enumerate(recommendations, 1):
                    rec_text += f"{i}. {rec['destination']} (Score: {rec['score']}) - {rec['reason']}\n"
                context_parts.append(rec_text)

        # Ajoute des données de l'API de voyage
        if "destination" in self.user_preferences:
            destination = self.user_preferences["destination"]
            api_recommendations = self.travel_api.get_recommendations(destination)

            if api_recommendations:
                api_text = f"\nAttractions populaires à {destination}:\n"
                for place in api_recommendations[:3]:
                    api_text += f"- {place['name']} (⭐ {place.get('rating', 'N/A')})\n"
                context_parts.append(api_text)

            # Ajoute des conseils pratiques
            if "preferred_activities" in self.user_preferences:
                tips = TravelHelpers.generate_travel_tips(
                    destination, self.user_preferences["preferred_activities"]
                )
                context_parts.append(
                    f"\nConseils pratiques:\n"
                    + "\n".join(f"• {tip}" for tip in tips[:3])
                )

        return "\n".join(context_parts)

    def _save_interaction(self, user_id: str, user_message: str, bot_response: str):
        """Sauvegarde l'interaction en base de données"""
        self.db.save_conversation(user_id, user_message, bot_response)
        self.db.update_user_preferences(user_id, self.user_preferences)

    def _generate_direct_openai_response(self, enriched_input: str) -> str:
        """Génère une réponse avec le client OpenAI direct"""
        try:
            from .prompts import EASY_TRAVEL_PROMPT

            # Utilise le prompt Easy Travel comme message système
            system_message = """Tu es Easy Travel, un assistant voyage intelligent et enthousiaste.
Tu aides les utilisateurs à planifier leurs voyages avec des recommandations personnalisées.
Réponds de manière amicale, informative et pratique."""

            response = self.direct_openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": enriched_input},
                ],
                max_tokens=800,
                temperature=0.7,
            )

            result = response.choices[0].message.content
            print("✅ Réponse générée via client OpenAI direct")
            return result

        except Exception as e:
            print(f"❌ Erreur client OpenAI direct: {e}")
            # Fallback vers le mode dégradé
            return self._generate_fallback_response(enriched_input, enriched_input)

    # ...existing code...

    def generate_travel_plan(self, user_id: str) -> dict:
        """Génère un plan de voyage personnalisé et enrichi avec toutes les données"""
        user_profile = self.db.get_user_profile_model(user_id)

        if not user_profile or not user_profile.preferences.preferred_destinations:
            return {
                "error": "Pas assez d'informations pour générer un plan. Mentionnez au moins une destination et vos préférences."
            }

        preferences = user_profile.preferences
        destination = preferences.preferred_destinations[0]  # Première destination

        # Données locales enrichies
        city_info = self.local_data_service.get_city_info(destination)
        local_attractions = self.local_data_service.get_local_attractions(destination)
        local_restaurants = self.local_data_service.get_local_restaurants(destination)
        transport_info = self.local_data_service.get_transport_info(destination)

        # Informations météo
        current_weather = self.weather_service.get_current_weather(destination)
        weather_forecast = self.weather_service.get_forecast(destination, 7)

        # Recommandations personnalisées
        personalized_recs = self.local_data_service.get_personalized_recommendations(
            destination, preferences.dict()
        )

        # Génère un itinéraire intelligent
        duration = self.user_preferences.get("duration_days", 7)  # 7 jours par défaut
        itinerary = self.recommendation_engine.generate_itinerary(
            destination, duration, preferences.preferred_activities
        )

        # Plan enrichi avec toutes les données
        enriched_plan = {
            "destination": destination,
            "durée_jours": duration,
            "budget_range": (
                preferences.budget_range.value
                if preferences.budget_range
                else "non spécifié"
            ),
            "type_voyage": (
                preferences.travel_type.value if preferences.travel_type else "loisir"
            ),
            # Informations de base de la ville
            "informations_ville": (
                {
                    "nom": city_info.name if city_info else destination,
                    "pays": city_info.country if city_info else "Non spécifié",
                    "monnaie": city_info.currency if city_info else "Non spécifié",
                    "langues": city_info.languages if city_info else [],
                    "urgences": city_info.emergency_numbers if city_info else {},
                    "pourboires": (
                        city_info.tipping_culture if city_info else "Non spécifié"
                    ),
                }
                if city_info
                else {"nom": destination}
            ),
            # Météo actuelle et prévisions
            "météo": {
                "actuelle": {
                    "température": (
                        f"{current_weather.temperature}°C"
                        if current_weather
                        else "Non disponible"
                    ),
                    "description": (
                        current_weather.description
                        if current_weather
                        else "Non disponible"
                    ),
                    "humidité": (
                        f"{current_weather.humidity}%"
                        if current_weather
                        else "Non disponible"
                    ),
                },
                "prévisions": (
                    [
                        {
                            "date": forecast.date,
                            "température_min": f"{forecast.temp_min}°C",
                            "température_max": f"{forecast.temp_max}°C",
                            "description": forecast.description,
                        }
                        for forecast in weather_forecast[:5]
                    ]
                    if weather_forecast
                    else []
                ),
            },
            # Attractions locales avec détails
            "attractions_recommandées": [
                {
                    "nom": attr.name,
                    "catégorie": attr.category,
                    "description": attr.description,
                    "adresse": attr.address,
                    "note": f"{attr.rating}/5",
                    "durée_visite": f"{attr.duration_visit} minutes",
                    "meilleur_moment": attr.best_time_visit,
                    "réservation_requise": attr.booking_required,
                }
                for attr in local_attractions[:8]
            ],
            # Restaurants avec spécialités
            "restaurants_suggérés": [
                {
                    "nom": rest.name,
                    "cuisine": rest.cuisine_type,
                    "description": rest.description,
                    "prix": rest.price_range,
                    "spécialités": rest.specialties[:3],
                    "ambiance": rest.atmosphere,
                    "favori_local": rest.local_favorite,
                }
                for rest in local_restaurants[:6]
            ],
            # Transport local
            "transport": (
                [
                    {
                        "type": trans.type,
                        "description": trans.description,
                        "coût": trans.cost,
                        "conseils": trans.tips[:2],
                    }
                    for trans in transport_info
                ]
                if transport_info
                else []
            ),
            # Conseils enrichis
            "conseils_pratiques": (
                city_info.cultural_etiquette + city_info.safety_tips
                if city_info
                else []
            )[:8],
            # Conseils météo personnalisés
            "conseils_météo": (
                self.weather_service.get_travel_weather_advice(
                    current_weather, preferences.preferred_activities
                )
                if current_weather
                else []
            ),
            # Itinéraire généré automatiquement
            "itinéraire_suggéré": itinerary,
            # Recommandations personnalisées
            "recommandations_personnalisées": personalized_recs,
            "généré_le": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # Sauvegarde le plan
        try:
            travel_plan = TravelPlan(
                user_id=user_id,
                destination=destination,
                duration_days=duration,
                budget_estimated=0.0,  # À calculer
                daily_activities=itinerary,
                accommodations=[],
                restaurants=[r for r in enriched_plan["restaurants_suggérés"]],
                practical_tips=enriched_plan["conseils_pratiques"],
            )
            self.db.save_travel_plan_model(travel_plan)
        except Exception as e:
            print(f"Erreur sauvegarde plan: {e}")

        return enriched_plan

    def get_smart_recommendations(self, user_id: str) -> dict:
        """Retourne des recommandations intelligentes basées sur le profil"""
        if not self.current_user_profile:
            return {"error": "Profil utilisateur non trouvé"}

        recommendations = self.recommendation_engine.get_personalized_recommendations(
            self.current_user_profile
        )

        return {
            "recommendations": recommendations,
            "based_on": {
                "activities": self.current_user_profile.preferences.preferred_activities,
                "budget": (
                    self.current_user_profile.preferences.budget_range.value
                    if self.current_user_profile.preferences.budget_range
                    else None
                ),
                "destinations": self.current_user_profile.preferences.preferred_destinations,
                "travel_type": (
                    self.current_user_profile.preferences.travel_type.value
                    if self.current_user_profile.preferences.travel_type
                    else None
                ),
            },
        }
