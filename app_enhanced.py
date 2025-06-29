import streamlit as st
import uuid
import json
from datetime import datetime, date
from chatbot.bot import EasyTravelChatbot
from services.interactive_journey import InteractiveJourneyOrchestrator, JourneyStage
from services.local_data_service import LocalDataService
from services.weather_service import WeatherService
from typing import Dict, Any, List

import os


# SOLUTION FINALE: Fix pour le problème OpenAI/httpx avec argument 'proxies'
def apply_openai_fix():
    """Applique le fix définitif pour OpenAI/httpx avant toute initialisation"""

    # Suppression complète des variables proxy
    proxy_vars = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
    ]
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]

    # Fix httpx pour supprimer l'argument 'proxies'
    try:
        import httpx

        # Fix pour Client synchrone
        if not hasattr(httpx.Client, "_easy_travel_fixed"):
            httpx.Client._easy_travel_fixed = True

            original_init = httpx.Client.__init__

            def fixed_init(self, *args, **kwargs):
                kwargs.pop("proxies", None)
                return original_init(self, *args, **kwargs)

            httpx.Client.__init__ = fixed_init

        # Fix pour AsyncClient asynchrone - CRITIQUE
        if not hasattr(httpx.AsyncClient, "_easy_travel_fixed"):
            httpx.AsyncClient._easy_travel_fixed = True

            original_async_init = httpx.AsyncClient.__init__

            def fixed_async_init(self, *args, **kwargs):
                kwargs.pop("proxies", None)
                return original_async_init(self, *args, **kwargs)

            httpx.AsyncClient.__init__ = fixed_async_init

        return True

    except Exception:
        return False


# Application du fix au démarrage de Streamlit
apply_openai_fix()

# Configuration proxy désactivée temporairement pour éviter les conflits OpenAI
# if os.getenv("HTTP_PROXY"):
#     os.environ["HTTP_PROXY"] = os.getenv("HTTP_PROXY")
# if os.getenv("HTTPS_PROXY"):
#     os.environ["HTTPS_PROXY"] = os.getenv("HTTPS_PROXY")


# Configuration de la page
st.set_page_config(
    page_title="Easy Travel - Assistant IA Intelligent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS amélioré pour l'interface
st.markdown(
    """
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

.journey-progress {
    background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
    height: 10px;
    border-radius: 5px;
    margin: 1rem 0;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 5px;
    transition: width 0.3s ease;
}

.journey-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

.activity-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s;
}

.activity-card:hover {
    transform: translateY(-2px);
}

.weather-widget {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    text-align: center;
}

.local-tip {
    background: rgba(255, 193, 7, 0.1);
    border-left: 4px solid #ffc107;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 10px 10px 0;
}

.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.user-message {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-left: 4px solid #2196f3;
}

.bot-message {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    border-left: 4px solid #9c27b0;
}

.recommendation-card {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialise les variables de session"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    if "chatbot" not in st.session_state:
        st.session_state.chatbot = EasyTravelChatbot()

    if "journey_orchestrator" not in st.session_state:
        st.session_state.journey_orchestrator = InteractiveJourneyOrchestrator()

    if "local_data_service" not in st.session_state:
        st.session_state.local_data_service = LocalDataService()

    if "weather_service" not in st.session_state:
        st.session_state.weather_service = WeatherService()

    if "journey_started" not in st.session_state:
        st.session_state.journey_started = False

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "selected_destination" not in st.session_state:
        st.session_state.selected_destination = None

    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "journey"  # "journey" ou "chat"


def render_header():
    """Affiche l'en-tête principal"""
    st.markdown(
        """
    <div class="main-header">
        <h1>✈️ Easy Travel Assistant Intelligent</h1>
        <p>Votre compagnon IA pour des voyages sur mesure enrichis de données locales</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Affiche la barre latérale avec les informations contextuelles"""
    with st.sidebar:
        st.header("🎯 Navigation")

        # Sélecteur de mode
        app_mode = st.radio(
            "Mode d'interaction",
            ["🗺️ Parcours guidé", "💬 Chat libre", "📊 Mes données"],
            key="mode_selector",
        )

        if app_mode == "🗺️ Parcours guidé":
            st.session_state.app_mode = "journey"
        elif app_mode == "💬 Chat libre":
            st.session_state.app_mode = "chat"
        else:
            st.session_state.app_mode = "data"

        # Progression du parcours si en mode guidé
        if st.session_state.app_mode == "journey" and st.session_state.journey_started:
            st.header("📈 Progression")
            progress_data = st.session_state.journey_orchestrator.get_user_progress(
                st.session_state.user_id
            )

            progress = progress_data.get("progress", 0)
            st.progress(progress / 100)
            st.write(f"**{progress:.0f}%** complété")
            st.write(
                f"**Étape actuelle:** {progress_data.get('current_step', 'Démarrage')}"
            )

            if progress_data.get("estimated_time_remaining", 0) > 0:
                st.write(
                    f"⏱️ **Temps estimé:** {progress_data['estimated_time_remaining']} min"
                )

        # Informations contextuelles
        if st.session_state.selected_destination:
            render_destination_sidebar()

        # Actions rapides
        st.header("🚀 Actions")

        if st.button("🆕 Nouveau parcours"):
            st.session_state.journey_orchestrator.reset_journey(
                st.session_state.user_id
            )
            st.session_state.journey_started = False
            st.session_state.messages = []
            st.rerun()

        if st.button("💾 Sauvegarder"):
            save_user_data()
            st.success("Données sauvegardées !")


def render_destination_sidebar():
    """Affiche les informations de destination dans la sidebar"""
    destination = st.session_state.selected_destination

    st.header(f"📍 {destination.title()}")

    # Météo actuelle
    weather = st.session_state.weather_service.get_current_weather(destination)
    if weather:
        st.markdown(
            f"""
        <div class="weather-widget">
            <h4>🌤️ Météo actuelle</h4>
            <p><strong>{weather.temperature:.1f}°C</strong></p>
            <p>{weather.description.title()}</p>
            <p>Ressenti: {weather.feels_like:.1f}°C</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Informations locales
    city_info = st.session_state.local_data_service.get_city_info(destination)
    if city_info:
        st.subheader("ℹ️ Infos pratiques")
        st.write(f"💰 **Monnaie:** {city_info.currency}")
        st.write(f"🗣️ **Langues:** {', '.join(city_info.languages)}")
        st.write(f"🚨 **Urgences:** {city_info.emergency_numbers.get('Police', 'N/A')}")

    # Conseils du jour
    attractions = st.session_state.local_data_service.get_local_attractions(destination)
    if attractions:
        st.subheader("💡 Conseil du jour")
        tip_attraction = attractions[0]  # Premier de la liste
        st.markdown(
            f"""
        <div class="local-tip">
            <strong>{tip_attraction.name}</strong><br>
            {tip_attraction.description[:100]}...
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_journey_mode():
    """Affiche le mode parcours guidé"""
    if not st.session_state.journey_started:
        # Page d'accueil du parcours
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(
                """
            <div class="journey-card">
                <h2>🌟 Créons votre voyage parfait</h2>
                <p>Notre parcours intelligent vous guide étape par étape pour créer un voyage 100% personnalisé.</p>
                <br>
                <h4>Ce que vous allez découvrir :</h4>
                <ul>
                    <li>🎯 Vos préférences de voyage</li>
                    <li>🗺️ Destinations adaptées à vos goûts</li>
                    <li>💰 Budget optimisé</li>
                    <li>🏨 Hébergements recommandés</li>
                    <li>🎪 Activités sur mesure</li>
                    <li>🌤️ Conseils météo en temps réel</li>
                    <li>🏛️ Données locales exclusives</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button(
                "🚀 Commencer mon parcours", type="primary", use_container_width=True
            ):
                st.session_state.journey_started = True
                st.session_state.journey_orchestrator.start_journey(
                    st.session_state.user_id
                )
                st.rerun()

    else:
        # Affichage du parcours en cours
        journey_data = st.session_state.journey_orchestrator.get_current_step_data(
            st.session_state.user_id
        )
        step = journey_data["step"]
        state = journey_data["state"]

        # En-tête de l'étape
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(
                f"""
            <div class="journey-card">
                <h2>{step.title}</h2>
                <p>{step.description}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            progress = journey_data["progress"]
            st.metric("Progression", f"{progress:.0f}%")

        # Question et interface de réponse
        st.markdown(f"### {step.question}")

        if step.help_text:
            st.info(step.help_text)

        # Interface adaptée au type d'étape
        render_step_interface(step, journey_data)


def render_step_interface(step, journey_data):
    """Affiche l'interface adaptée au type d'étape"""

    if step.ui_type == "multiple_choice":
        render_multiple_choice_interface(step, journey_data)

    elif step.ui_type == "slider":
        render_slider_interface(step, journey_data)

    elif step.ui_type == "date_picker":
        render_date_picker_interface(step, journey_data)

    elif step.ui_type == "summary_confirmation":
        render_summary_interface(step, journey_data)

    elif step.ui_type == "plan_display":
        render_plan_display_interface(step, journey_data)

    else:
        # Interface texte par défaut
        render_text_interface(step, journey_data)


def render_multiple_choice_interface(step, journey_data):
    """Interface de choix multiple avec cartes visuelles"""

    if step.options:
        # Affichage en colonnes pour les options
        cols = st.columns(min(len(step.options), 3))

        selected_option = None

        for i, option in enumerate(step.options):
            with cols[i % 3]:
                if st.button(
                    f"{option.get('emoji', '')} {option['label']}",
                    key=f"option_{i}",
                    help=option.get("description", ""),
                    use_container_width=True,
                ):
                    selected_option = option

        if selected_option:
            # Traitement de la réponse
            response = {
                "value": selected_option["value"],
                "label": selected_option["label"],
            }

            # Si c'est une étape de sélection d'activités, permettre la sélection multiple
            if step.id == "activities_deep_dive":
                if "selected_activities" not in st.session_state:
                    st.session_state.selected_activities = []

                if selected_option["value"] not in st.session_state.selected_activities:
                    st.session_state.selected_activities.append(
                        selected_option["value"]
                    )

                st.success(f"Activité ajoutée : {selected_option['label']}")

                if len(st.session_state.selected_activities) >= 3:
                    if st.button("✅ Continuer avec mes activités", type="primary"):
                        response = {
                            "priority_activities": st.session_state.selected_activities
                        }
                        process_journey_response(response)
                        st.session_state.selected_activities = []
                else:
                    st.info(
                        f"Sélectionnez encore {3 - len(st.session_state.selected_activities)} activité(s)"
                    )
            else:
                process_journey_response(response)


def render_slider_interface(step, journey_data):
    """Interface avec slider pour le budget"""
    if step.options:
        budget_labels = [opt["range"] for opt in step.options]
        budget_values = [opt["value"] for opt in step.options]

        selected_index = st.select_slider(
            "Sélectionnez votre budget",
            options=list(range(len(budget_labels))),
            format_func=lambda x: f"{budget_labels[x]} - {step.options[x]['description']}",
        )

        if st.button("💰 Confirmer mon budget", type="primary"):
            response = {
                "budget_amount": budget_values[selected_index],
                "budget_range": step.options[selected_index]["range"],
            }
            process_journey_response(response)


def render_date_picker_interface(step, journey_data):
    """Interface de sélection de dates"""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Durée du voyage")
        if step.options:
            duration_options = [(opt["value"], opt["label"]) for opt in step.options]
            selected_duration = st.selectbox(
                "Combien de temps ?", duration_options, format_func=lambda x: x[1]
            )

    with col2:
        st.subheader("🗓️ Dates préférées")
        start_date = st.date_input("Date de départ souhaitée")
        flexible = st.checkbox("Mes dates sont flexibles")

    if st.button("📅 Confirmer mes dates", type="primary"):
        response = {
            "trip_duration": selected_duration[0],
            "preferred_dates": start_date.isoformat(),
            "date_flexibility": flexible,
        }
        process_journey_response(response)


def render_summary_interface(step, journey_data):
    """Interface de résumé des préférences"""
    state = journey_data["state"]
    collected_data = state.collected_data

    st.subheader("📋 Récapitulatif de votre profil voyage")

    # Affichage du profil
    col1, col2 = st.columns(2)

    with col1:
        if "traveler_type" in collected_data:
            st.metric("Type de voyageur", collected_data["traveler_type"].title())

        if "budget_amount" in collected_data:
            st.metric("Budget", collected_data["budget_amount"].title())

        if "trip_duration" in collected_data:
            st.metric("Durée", collected_data["trip_duration"].title())

    with col2:
        if "priority_activities" in collected_data:
            activities = collected_data["priority_activities"]
            st.write("🎯 **Activités préférées:**")
            for activity in activities:
                st.write(f"• {activity.title()}")

        if "accommodation_preference" in collected_data:
            st.metric("Hébergement", collected_data["accommodation_preference"].title())

    # Boutons d'action
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✏️ Modifier mes préférences", use_container_width=True):
            st.session_state.journey_orchestrator.reset_journey(
                st.session_state.user_id
            )
            st.rerun()

    with col2:
        if st.button(
            "🎉 Générer mon voyage !", type="primary", use_container_width=True
        ):
            response = {"profile_confirmation": True}
            process_journey_response(response)


def render_plan_display_interface(step, journey_data):
    """Interface d'affichage du plan généré"""
    state = journey_data["state"]

    # Génération du plan avec toutes les données enrichies
    plan_data = generate_enriched_travel_plan(state.collected_data)

    st.markdown("## 🎉 Votre voyage sur mesure est prêt !")

    # Onglets pour organiser les informations
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Itinéraire", "🌤️ Météo", "🏛️ Local", "💡 Conseils"]
    )

    with tab1:
        render_itinerary_tab(plan_data)

    with tab2:
        render_weather_tab(plan_data)

    with tab3:
        render_local_tab(plan_data)

    with tab4:
        render_tips_tab(plan_data)

    # Actions sur le plan
    st.subheader("Que souhaitez-vous faire maintenant ?")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✏️ Ajuster", use_container_width=True):
            response = {"next_action": "refine"}
            process_journey_response(response)

    with col2:
        if st.button("📞 Réserver", use_container_width=True):
            response = {"next_action": "book"}
            process_journey_response(response)

    with col3:
        if st.button("💾 Sauvegarder", use_container_width=True):
            save_travel_plan(plan_data)
            st.success("Plan sauvegardé !")

    with col4:
        if st.button("📤 Partager", use_container_width=True):
            share_travel_plan(plan_data)


def render_text_interface(step, journey_data):
    """Interface texte par défaut"""
    user_input = st.text_area("Votre réponse:", height=100)

    if st.button("➡️ Continuer", type="primary"):
        if user_input.strip():
            process_journey_response(user_input)
        else:
            st.error("Veuillez saisir une réponse")


def process_journey_response(response):
    """Traite la réponse utilisateur dans le parcours"""
    next_step_data = st.session_state.journey_orchestrator.process_user_response(
        st.session_state.user_id, response
    )

    # Mise à jour de la destination sélectionnée si disponible
    state = next_step_data["state"]
    if "destination" in state.collected_data:
        st.session_state.selected_destination = state.collected_data["destination"]

    st.rerun()


def generate_enriched_travel_plan(collected_data: Dict[str, Any]) -> Dict[str, Any]:
    """Génère un plan de voyage enrichi avec toutes les données locales"""

    # Utilise le chatbot pour la génération de base
    plan_result = st.session_state.chatbot.generate_travel_plan(
        st.session_state.user_id
    )

    destination = collected_data.get("destination", "Paris")

    # Enrichissement avec données locales
    local_data = st.session_state.local_data_service.get_personalized_recommendations(
        destination, collected_data
    )

    # Données météo
    weather_current = st.session_state.weather_service.get_current_weather(destination)
    weather_forecast = st.session_state.weather_service.get_forecast(destination, 7)

    enriched_plan = {
        "base_plan": plan_result,
        "destination": destination,
        "local_attractions": local_data.get("attractions", []),
        "local_restaurants": local_data.get("restaurants", []),
        "weather_current": weather_current,
        "weather_forecast": weather_forecast,
        "local_tips": local_data.get("tips", []),
        "transport_info": st.session_state.local_data_service.get_transport_info(
            destination
        ),
        "events": st.session_state.local_data_service.get_local_events(destination),
    }

    return enriched_plan


def render_itinerary_tab(plan_data):
    """Affiche l'onglet itinéraire"""
    st.subheader(f"📍 Destination: {plan_data['destination'].title()}")

    # Plan de base généré par l'IA
    if "base_plan" in plan_data and "plan" in plan_data["base_plan"]:
        base_plan = plan_data["base_plan"]["plan"]
        if isinstance(base_plan, dict):
            st.json(base_plan)
        else:
            st.write(base_plan)

    # Attractions locales recommandées
    if plan_data["local_attractions"]:
        st.subheader("🏛️ Attractions recommandées pour vous")
        for attraction in plan_data["local_attractions"][:3]:
            with st.expander(f"⭐ {attraction.name} - Note: {attraction.rating}/5"):
                st.write(attraction.description)
                st.write(f"📍 **Adresse:** {attraction.address}")
                st.write(f"⏱️ **Durée de visite:** {attraction.duration_visit} minutes")
                st.write(f"🕒 **Meilleur moment:** {attraction.best_time_visit}")
                if attraction.booking_required:
                    st.warning("⚠️ Réservation obligatoire")


def render_weather_tab(plan_data):
    """Affiche l'onglet météo"""
    weather_current = plan_data["weather_current"]
    weather_forecast = plan_data["weather_forecast"]

    if weather_current:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🌡️ Température", f"{weather_current.temperature:.1f}°C")

        with col2:
            st.metric("🌡️ Ressenti", f"{weather_current.feels_like:.1f}°C")

        with col3:
            st.metric("💧 Humidité", f"{weather_current.humidity}%")

        with col4:
            st.metric("💨 Vent", f"{weather_current.wind_speed:.1f} m/s")

        st.write(f"☁️ **Conditions:** {weather_current.description.title()}")

        if weather_current.sunrise and weather_current.sunset:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"🌅 **Lever du soleil:** {weather_current.sunrise}")
            with col2:
                st.write(f"🌇 **Coucher du soleil:** {weather_current.sunset}")

    if weather_forecast:
        st.subheader("📅 Prévisions sur 7 jours")

        for forecast in weather_forecast:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write(f"**{forecast.date}**")

            with col2:
                st.write(f"🌡️ {forecast.temp_min:.0f}°C - {forecast.temp_max:.0f}°C")

            with col3:
                st.write(f"☁️ {forecast.description}")

            with col4:
                st.write(f"🌧️ {forecast.precipitation_chance}%")


def render_local_tab(plan_data):
    """Affiche l'onglet données locales"""

    # Restaurants recommandés
    if plan_data["local_restaurants"]:
        st.subheader("🍽️ Restaurants recommandés")
        for restaurant in plan_data["local_restaurants"]:
            with st.expander(f"{restaurant.name} - {restaurant.price_range}"):
                st.write(f"🍳 **Cuisine:** {restaurant.cuisine_type}")
                st.write(f"⭐ **Note:** {restaurant.rating}/5")
                st.write(f"📍 **Adresse:** {restaurant.address}")
                st.write(f"🍽️ **Spécialités:** {', '.join(restaurant.specialties)}")
                if restaurant.local_favorite:
                    st.success("👥 Favori des locaux !")

    # Informations transport
    if plan_data["transport_info"]:
        st.subheader("🚇 Transport local")
        for transport in plan_data["transport_info"]:
            with st.expander(f"{transport.type} - {transport.cost}"):
                st.write(transport.description)
                st.write(f"⏱️ **Durée:** {transport.duration}")
                st.write(f"🔄 **Fréquence:** {transport.frequency}")

                if transport.tips:
                    st.write("💡 **Conseils:**")
                    for tip in transport.tips:
                        st.write(f"• {tip}")

    # Événements locaux
    if plan_data["events"]:
        st.subheader("🎪 Événements locaux")
        for event in plan_data["events"]:
            with st.expander(f"{event.name} - {event.start_date}"):
                st.write(event.description)
                st.write(f"📅 **Dates:** {event.start_date} - {event.end_date}")
                st.write(f"📍 **Lieu:** {event.location}")
                if event.price:
                    st.write(f"💰 **Prix:** {event.price}")


def render_tips_tab(plan_data):
    """Affiche l'onglet conseils"""

    # Conseils locaux
    if plan_data["local_tips"]:
        st.subheader("💡 Conseils locaux")
        for tip in plan_data["local_tips"]:
            st.info(f"💡 {tip}")

    # Conseils météo
    if plan_data["weather_current"]:
        weather_advice = st.session_state.weather_service.get_travel_weather_advice(
            plan_data["weather_current"],
            ["culture", "nature"],  # À adapter selon les préférences
        )

        if weather_advice:
            st.subheader("🌤️ Conseils météo")
            for advice in weather_advice:
                st.info(advice)

    # Conseils généraux
    general_tips = [
        "📱 Téléchargez l'application de transport local",
        "💳 Vérifiez si votre carte bancaire fonctionne à l'étranger",
        "📄 Conservez une copie de vos documents importants",
        "🏥 Notez les numéros d'urgence locaux",
        "🗣️ Apprenez quelques mots de base dans la langue locale",
    ]

    st.subheader("🎯 Conseils généraux")
    for tip in general_tips:
        st.write(tip)


def render_chat_mode():
    """Affiche le mode chat libre"""
    st.subheader("💬 Chat libre avec Easy Travel")

    # Affichage des messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f"""
            <div class="chat-message user-message">
                <strong>Vous:</strong> {message["content"]}
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="chat-message bot-message">
                <strong>Easy Travel:</strong> {message["content"]}
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Interface de chat
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Posez-moi toutes vos questions voyage...", key="chat_input"
        )
        submitted = st.form_submit_button("Envoyer")

        if submitted and user_input:
            # Ajoute le message utilisateur
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Génère la réponse du chatbot
            with st.spinner("Easy Travel réfléchit..."):
                response = st.session_state.chatbot.process_message(
                    user_input, st.session_state.user_id
                )

            # Ajoute la réponse du bot
            st.session_state.messages.append({"role": "assistant", "content": response})

            st.rerun()


def render_data_mode():
    """Affiche le mode données utilisateur"""
    st.subheader("📊 Mes données de voyage")

    # Résumé du parcours
    if st.session_state.journey_started:
        journey_summary = st.session_state.journey_orchestrator.get_journey_summary(
            st.session_state.user_id
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "⏱️ Temps de parcours",
                f"{journey_summary.get('journey_duration', 0):.1f} min",
            )

        with col2:
            st.metric(
                "📈 Progression",
                f"{journey_summary.get('completion_rate', 0)*100:.0f}%",
            )

        with col3:
            st.metric(
                "🎯 Personnalisation",
                f"{journey_summary.get('personalization_level', 0):.0f}%",
            )

        with col4:
            collected_points = len(journey_summary.get("collected_preferences", {}))
            st.metric("📋 Données collectées", f"{collected_points} points")

        # Profil utilisateur
        if "user_profile" in journey_summary:
            st.subheader("👤 Votre profil voyage")
            profile = journey_summary["user_profile"]

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    f"**Type de voyageur:** {profile.get('traveler_type', 'Non défini')}"
                )
                st.write(
                    f"**Budget préféré:** {profile.get('budget_range', 'Non défini')}"
                )
                st.write(
                    f"**Durée habituelle:** {profile.get('trip_duration', 'Non défini')}"
                )

            with col2:
                activities = profile.get("preferred_activities", [])
                if activities:
                    st.write("**Activités préférées:**")
                    for activity in activities:
                        st.write(f"• {activity}")

                st.write(
                    f"**Style d'hébergement:** {profile.get('accommodation_style', 'Non défini')}"
                )

    # Historique des conversations
    st.subheader("💬 Historique des conversations")
    if st.session_state.messages:
        for i, message in enumerate(
            st.session_state.messages[-5:], 1
        ):  # Derniers 5 messages
            role = "Vous" if message["role"] == "user" else "Assistant"
            st.text(f"{i}. {role}: {message['content'][:100]}...")
    else:
        st.info("Aucune conversation enregistrée")


def save_user_data():
    """Sauvegarde les données utilisateur"""
    # Cette fonction pourrait sauvegarder en base de données
    if st.session_state.journey_started:
        journey_summary = st.session_state.journey_orchestrator.get_journey_summary(
            st.session_state.user_id
        )
        # Sauvegarde en session pour l'exemple
        st.session_state["saved_data"] = journey_summary


def save_travel_plan(plan_data):
    """Sauvegarde un plan de voyage"""
    # Implémentation de sauvegarde
    pass


def share_travel_plan(plan_data):
    """Partage un plan de voyage"""
    st.info("Fonctionnalité de partage à venir !")


def main():
    """Fonction principale"""
    initialize_session_state()
    render_header()
    render_sidebar()

    # Affichage selon le mode sélectionné
    if st.session_state.app_mode == "journey":
        render_journey_mode()
    elif st.session_state.app_mode == "chat":
        render_chat_mode()
    elif st.session_state.app_mode == "data":
        render_data_mode()


if __name__ == "__main__":
    main()
