from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import json


class JourneyStage(Enum):
    WELCOME = "welcome"
    PROFILE_DISCOVERY = "profile_discovery"
    DESTINATION_SELECTION = "destination_selection"
    PREFERENCES_DETAILS = "preferences_details"
    BUDGET_PLANNING = "budget_planning"
    DATE_SELECTION = "date_selection"
    ACTIVITIES_SELECTION = "activities_selection"
    ACCOMMODATION_PREFERENCES = "accommodation_preferences"
    PLAN_GENERATION = "plan_generation"
    PLAN_REFINEMENT = "plan_refinement"
    BOOKING_GUIDANCE = "booking_guidance"
    FINAL_CHECKLIST = "final_checklist"


@dataclass
class JourneyStep:
    id: str
    stage: JourneyStage
    title: str
    description: str
    question: str
    expected_inputs: List[str]
    next_steps: Dict[str, str]  # conditions -> next_step_id
    data_to_collect: List[str]
    ui_type: str  # "text", "multiple_choice", "slider", "date_picker", "map"
    options: Optional[List[Dict[str, Any]]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    help_text: Optional[str] = None
    tips: Optional[List[str]] = None


@dataclass
class UserJourneyState:
    user_id: str
    current_step: str
    completed_steps: List[str]
    collected_data: Dict[str, Any]
    journey_start_time: datetime
    last_interaction_time: datetime
    stage_completion_times: Dict[str, datetime]
    personalized_options: Dict[str, List[Any]]


class InteractiveJourneyOrchestrator:
    def __init__(self):
        self.journey_steps = self._initialize_journey_steps()
        self.user_states: Dict[str, UserJourneyState] = {}

    def _initialize_journey_steps(self) -> Dict[str, JourneyStep]:
        """Initialise toutes les étapes du parcours interactif"""

        steps = {
            "welcome": JourneyStep(
                id="welcome",
                stage=JourneyStage.WELCOME,
                title="🌍 Bienvenue chez Easy Travel !",
                description="Commençons votre aventure personnalisée",
                question="Bonjour ! Je suis votre assistant voyage personnel. Pour vous proposer l'expérience parfaite, j'ai quelques questions. Êtes-vous prêt(e) à découvrir votre prochain voyage de rêve ?",
                expected_inputs=["oui", "yes", "prêt", "commencer", "go"],
                next_steps={"positive": "profile_discovery"},
                data_to_collect=["user_readiness"],
                ui_type="multiple_choice",
                options=[
                    {"value": "yes", "label": "🚀 Oui, commençons !", "emoji": "🚀"},
                    {
                        "value": "info",
                        "label": "📋 D'abord, expliquez-moi",
                        "emoji": "📋",
                    },
                    {"value": "quick", "label": "⚡ Mode rapide", "emoji": "⚡"},
                ],
                help_text="Ce parcours prend environ 5-10 minutes et vous aidera à créer un voyage sur mesure.",
            ),
            "profile_discovery": JourneyStep(
                id="profile_discovery",
                stage=JourneyStage.PROFILE_DISCOVERY,
                title="👤 Apprenons à nous connaître",
                description="Parlez-moi de vous pour personnaliser vos recommandations",
                question="Pour mieux vous connaître, pouvez-vous me dire quel type de voyageur vous êtes ?",
                expected_inputs=[
                    "aventurier",
                    "culturel",
                    "détente",
                    "famille",
                    "romantique",
                    "business",
                ],
                next_steps={"any": "destination_exploration"},
                data_to_collect=[
                    "traveler_type",
                    "travel_experience",
                    "preferred_style",
                ],
                ui_type="multiple_choice",
                options=[
                    {
                        "value": "aventurier",
                        "label": "🏔️ Aventurier",
                        "description": "J'aime l'action et les expériences uniques",
                    },
                    {
                        "value": "culturel",
                        "label": "🏛️ Explorateur culturel",
                        "description": "Histoire, art, traditions locales",
                    },
                    {
                        "value": "detente",
                        "label": "🏖️ Recherche de détente",
                        "description": "Repos, spa, plages paradisiaques",
                    },
                    {
                        "value": "famille",
                        "label": "👨‍👩‍👧‍👦 Voyage en famille",
                        "description": "Activités pour tous les âges",
                    },
                    {
                        "value": "romantique",
                        "label": "💕 Escapade romantique",
                        "description": "Moments intimes et romantiques",
                    },
                    {
                        "value": "business",
                        "label": "💼 Voyageur d'affaires",
                        "description": "Efficacité et confort",
                    },
                ],
                tips=[
                    "Vous pouvez combiner plusieurs styles !",
                    "Pas de souci si vous hésitez, nous ajusterons en cours de route",
                ],
            ),
            "destination_exploration": JourneyStep(
                id="destination_exploration",
                stage=JourneyStage.DESTINATION_SELECTION,
                title="🗺️ Où rêvez-vous d'aller ?",
                description="Découvrons votre destination idéale",
                question="Avez-vous déjà une destination en tête, ou souhaitez-vous que je vous propose des idées basées sur vos goûts ?",
                expected_inputs=["destination_précise", "suggestions", "inspiration"],
                next_steps={
                    "has_destination": "destination_details",
                    "wants_suggestions": "destination_quiz",
                    "needs_inspiration": "inspiration_mode",
                },
                data_to_collect=["destination_preference_type"],
                ui_type="multiple_choice",
                options=[
                    {
                        "value": "has_destination",
                        "label": "📍 J'ai déjà une idée précise",
                        "emoji": "📍",
                    },
                    {
                        "value": "wants_suggestions",
                        "label": "💡 Proposez-moi des options",
                        "emoji": "💡",
                    },
                    {
                        "value": "needs_inspiration",
                        "label": "✨ Surprenez-moi !",
                        "emoji": "✨",
                    },
                ],
            ),
            "destination_quiz": JourneyStep(
                id="destination_quiz",
                stage=JourneyStage.DESTINATION_SELECTION,
                title="🎯 Quiz destination parfaite",
                description="Répondez à ces questions pour trouver votre destination idéale",
                question="Quel climat préférez-vous pour vos vacances ?",
                expected_inputs=["climat"],
                next_steps={"any": "budget_exploration"},
                data_to_collect=[
                    "preferred_climate",
                    "landscape_preference",
                    "culture_interest",
                ],
                ui_type="multiple_choice",
                options=[
                    {
                        "value": "tropical",
                        "label": "🌴 Tropical (chaud et humide)",
                        "temp": "25-35°C",
                    },
                    {
                        "value": "mediterranean",
                        "label": "☀️ Méditerranéen (chaud et sec)",
                        "temp": "20-30°C",
                    },
                    {
                        "value": "temperate",
                        "label": "🌤️ Tempéré (doux)",
                        "temp": "15-25°C",
                    },
                    {
                        "value": "mountain",
                        "label": "🏔️ Montagnard (frais)",
                        "temp": "5-20°C",
                    },
                    {
                        "value": "desert",
                        "label": "🏜️ Désertique (contrasté)",
                        "temp": "Variable",
                    },
                ],
            ),
            "budget_exploration": JourneyStep(
                id="budget_exploration",
                stage=JourneyStage.BUDGET_PLANNING,
                title="💰 Planifions votre budget",
                description="Définissons un budget confortable pour votre voyage",
                question="Quel budget envisagez-vous pour votre voyage (par personne, transport inclus) ?",
                expected_inputs=["budget_range"],
                next_steps={"any": "duration_selection"},
                data_to_collect=[
                    "budget_amount",
                    "budget_flexibility",
                    "priority_spending",
                ],
                ui_type="slider",
                options=[
                    {
                        "value": "low",
                        "range": "300-800€",
                        "description": "Budget serré, maximiser les expériences",
                    },
                    {
                        "value": "medium",
                        "range": "800-2000€",
                        "description": "Budget équilibré, confort et découvertes",
                    },
                    {
                        "value": "high",
                        "range": "2000-5000€",
                        "description": "Budget généreux, expériences premium",
                    },
                    {
                        "value": "luxury",
                        "range": "5000€+",
                        "description": "Budget illimité, luxe et exclusivité",
                    },
                ],
                help_text="Votre budget nous aide à filtrer les meilleures options pour vous.",
            ),
            "duration_selection": JourneyStep(
                id="duration_selection",
                stage=JourneyStage.DATE_SELECTION,
                title="📅 Quand et combien de temps ?",
                description="Planifions les dates de votre voyage",
                question="Combien de temps souhaitez-vous partir et avez-vous des contraintes de dates ?",
                expected_inputs=["duration", "dates", "flexibility"],
                next_steps={"any": "activities_deep_dive"},
                data_to_collect=[
                    "trip_duration",
                    "preferred_dates",
                    "date_flexibility",
                    "season_preference",
                ],
                ui_type="date_picker",
                options=[
                    {
                        "value": "weekend",
                        "label": "🏃‍♂️ Week-end (2-3 jours)",
                        "ideal_for": "Escapade rapide",
                    },
                    {
                        "value": "short",
                        "label": "⚡ Court séjour (4-7 jours)",
                        "ideal_for": "Découverte ciblée",
                    },
                    {
                        "value": "medium",
                        "label": "🌟 Séjour classique (1-2 semaines)",
                        "ideal_for": "Exploration complète",
                    },
                    {
                        "value": "long",
                        "label": "🌍 Long voyage (3+ semaines)",
                        "ideal_for": "Immersion totale",
                    },
                ],
            ),
            "activities_deep_dive": JourneyStep(
                id="activities_deep_dive",
                stage=JourneyStage.ACTIVITIES_SELECTION,
                title="🎯 Vos activités passions",
                description="Sélectionnez ce qui vous fait vibrer en voyage",
                question="Quelles activités vous enthousiasment le plus ? (Sélectionnez plusieurs options)",
                expected_inputs=["activities"],
                next_steps={"any": "accommodation_style"},
                data_to_collect=[
                    "priority_activities",
                    "activity_intensity",
                    "group_activities",
                ],
                ui_type="multiple_choice",
                options=[
                    {
                        "value": "culture",
                        "label": "🏛️ Culture & Histoire",
                        "sub": ["Musées", "Monuments", "Sites historiques"],
                    },
                    {
                        "value": "nature",
                        "label": "🌿 Nature & Aventure",
                        "sub": ["Randonnée", "Parcs", "Paysages"],
                    },
                    {
                        "value": "gastronomie",
                        "label": "🍷 Gastronomie",
                        "sub": ["Restaurants", "Marchés", "Cours de cuisine"],
                    },
                    {
                        "value": "nightlife",
                        "label": "🌙 Vie nocturne",
                        "sub": ["Bars", "Clubs", "Spectacles"],
                    },
                    {
                        "value": "shopping",
                        "label": "🛍️ Shopping",
                        "sub": ["Boutiques", "Marchés", "Souvenirs"],
                    },
                    {
                        "value": "detente",
                        "label": "🧘‍♀️ Détente & Bien-être",
                        "sub": ["Spa", "Plages", "Yoga"],
                    },
                    {
                        "value": "sport",
                        "label": "⚽ Sports",
                        "sub": ["Vélo", "Sports nautiques", "Fitness"],
                    },
                    {
                        "value": "art",
                        "label": "🎨 Art & Créativité",
                        "sub": ["Galeries", "Ateliers", "Street art"],
                    },
                ],
                help_text="Sélectionnez 3-5 activités qui vous passionnent vraiment.",
            ),
            "accommodation_style": JourneyStep(
                id="accommodation_style",
                stage=JourneyStage.ACCOMMODATION_PREFERENCES,
                title="🏨 Votre style d'hébergement",
                description="Quel type de logement vous correspond ?",
                question="Où préférez-vous séjourner pour vous sentir bien ?",
                expected_inputs=["accommodation_type"],
                next_steps={"any": "personalization_summary"},
                data_to_collect=[
                    "accommodation_preference",
                    "location_priority",
                    "amenities_important",
                ],
                ui_type="multiple_choice",
                options=[
                    {
                        "value": "hotel_luxury",
                        "label": "🏰 Hôtel de luxe",
                        "description": "Service premium, confort maximal",
                    },
                    {
                        "value": "hotel_boutique",
                        "label": "🏨 Hôtel boutique",
                        "description": "Charme, design, expérience unique",
                    },
                    {
                        "value": "apartment",
                        "label": "🏠 Appartement/Airbnb",
                        "description": "Comme à la maison, flexibilité",
                    },
                    {
                        "value": "hostel",
                        "label": "🎒 Auberge de jeunesse",
                        "description": "Économique, rencontres, convivial",
                    },
                    {
                        "value": "authentic",
                        "label": "🏡 Logement authentique",
                        "description": "Chez l'habitant, immersion locale",
                    },
                    {
                        "value": "resort",
                        "label": "🏖️ Resort tout inclus",
                        "description": "Tout sur place, relaxation totale",
                    },
                ],
            ),
            "personalization_summary": JourneyStep(
                id="personalization_summary",
                stage=JourneyStage.PLAN_GENERATION,
                title="✨ Votre profil voyage personnalisé",
                description="Récapitulatif de vos préférences",
                question="Parfait ! Voici votre profil voyage. Souhaitez-vous que je génère votre plan personnalisé ?",
                expected_inputs=["confirmation", "modification"],
                next_steps={
                    "generate": "plan_presentation",
                    "modify": "preference_modification",
                },
                data_to_collect=["profile_confirmation"],
                ui_type="summary_confirmation",
                help_text="Vous pourrez toujours ajuster votre plan après génération.",
            ),
            "plan_presentation": JourneyStep(
                id="plan_presentation",
                stage=JourneyStage.PLAN_GENERATION,
                title="🎉 Votre voyage sur mesure est prêt !",
                description="Plan détaillé basé sur vos préférences",
                question="Voici votre plan de voyage personnalisé ! Que souhaitez-vous faire ?",
                expected_inputs=["action"],
                next_steps={
                    "refine": "plan_refinement",
                    "book": "booking_guidance",
                    "save": "plan_saving",
                    "share": "plan_sharing",
                },
                data_to_collect=["plan_feedback", "next_action"],
                ui_type="plan_display",
                options=[
                    {
                        "value": "refine",
                        "label": "✏️ Ajuster le plan",
                        "description": "Modifier certains éléments",
                    },
                    {
                        "value": "book",
                        "label": "📞 Guide de réservation",
                        "description": "Aide pour réserver",
                    },
                    {
                        "value": "save",
                        "label": "💾 Sauvegarder",
                        "description": "Garder pour plus tard",
                    },
                    {
                        "value": "share",
                        "label": "📤 Partager",
                        "description": "Envoyer à des amis",
                    },
                ],
            ),
            "plan_refinement": JourneyStep(
                id="plan_refinement",
                stage=JourneyStage.PLAN_REFINEMENT,
                title="🔧 Ajustons votre plan",
                description="Personnalisation fine de votre voyage",
                question="Que souhaitez-vous modifier dans votre plan ?",
                expected_inputs=["modification_type"],
                next_steps={
                    "activities": "activity_adjustment",
                    "accommodation": "accommodation_adjustment",
                    "budget": "budget_adjustment",
                    "timing": "timing_adjustment",
                },
                data_to_collect=["modification_requests"],
                ui_type="multiple_choice",
                options=[
                    {
                        "value": "activities",
                        "label": "🎯 Activités",
                        "description": "Changer les lieux/expériences",
                    },
                    {
                        "value": "accommodation",
                        "label": "🏨 Hébergement",
                        "description": "Type ou localisation",
                    },
                    {
                        "value": "budget",
                        "label": "💰 Budget",
                        "description": "Ajuster les coûts",
                    },
                    {
                        "value": "timing",
                        "label": "⏰ Planning",
                        "description": "Modifier les horaires",
                    },
                ],
            ),
            "booking_guidance": JourneyStep(
                id="booking_guidance",
                stage=JourneyStage.BOOKING_GUIDANCE,
                title="📞 Guide de réservation",
                description="Je vous accompagne pour concrétiser votre voyage",
                question="Quel type d'aide souhaitez-vous pour vos réservations ?",
                expected_inputs=["booking_help_type"],
                next_steps={"any": "final_checklist"},
                data_to_collect=["booking_preferences", "help_needed"],
                ui_type="multiple_choice",
                options=[
                    {
                        "value": "links",
                        "label": "🔗 Liens directs",
                        "description": "Sites de réservation recommandés",
                    },
                    {
                        "value": "tips",
                        "label": "💡 Conseils de réservation",
                        "description": "Meilleurs moments, astuces",
                    },
                    {
                        "value": "comparison",
                        "label": "⚖️ Comparaison des options",
                        "description": "Aide au choix",
                    },
                    {
                        "value": "calendar",
                        "label": "📅 Planification",
                        "description": "Ordre des réservations",
                    },
                ],
            ),
            "final_checklist": JourneyStep(
                id="final_checklist",
                stage=JourneyStage.FINAL_CHECKLIST,
                title="✅ Checklist finale",
                description="Tout est prêt pour votre aventure !",
                question="Voici votre checklist personnalisée. Votre voyage Easy Travel est organisé !",
                expected_inputs=["completion"],
                next_steps={"complete": "journey_complete"},
                data_to_collect=["checklist_completion"],
                ui_type="checklist",
                tips=[
                    "Gardez cette checklist accessible",
                    "Contactez-nous si vous avez des questions",
                    "Bon voyage ! 🌍✈️",
                ],
            ),
        }

        return steps

    def start_journey(self, user_id: str) -> Dict[str, Any]:
        """Démarre un nouveau parcours pour un utilisateur"""
        self.user_states[user_id] = UserJourneyState(
            user_id=user_id,
            current_step="welcome",
            completed_steps=[],
            collected_data={},
            journey_start_time=datetime.now(),
            last_interaction_time=datetime.now(),
            stage_completion_times={},
            personalized_options={},
        )

        return self.get_current_step_data(user_id)

    def get_current_step_data(self, user_id: str) -> Dict[str, Any]:
        """Récupère les données de l'étape actuelle"""
        if user_id not in self.user_states:
            return self.start_journey(user_id)

        state = self.user_states[user_id]
        current_step = self.journey_steps[state.current_step]

        return {
            "step": current_step,
            "state": state,
            "progress": len(state.completed_steps) / len(self.journey_steps) * 100,
            "personalized_content": self._get_personalized_content(
                user_id, current_step
            ),
        }

    def process_user_response(self, user_id: str, response: Any) -> Dict[str, Any]:
        """Traite la réponse utilisateur et détermine l'étape suivante"""
        if user_id not in self.user_states:
            return self.start_journey(user_id)

        state = self.user_states[user_id]
        current_step = self.journey_steps[state.current_step]

        # Sauvegarde la réponse
        for data_key in current_step.data_to_collect:
            if isinstance(response, dict):
                state.collected_data[data_key] = response.get(data_key, response)
            else:
                state.collected_data[data_key] = response

        # Détermine l'étape suivante
        next_step_id = self._determine_next_step(current_step, response, state)

        # Met à jour l'état
        state.completed_steps.append(state.current_step)
        state.current_step = next_step_id
        state.last_interaction_time = datetime.now()

        # Marque la fin d'une étape
        if current_step.stage not in state.stage_completion_times:
            state.stage_completion_times[current_step.stage] = datetime.now()

        return self.get_current_step_data(user_id)

    def _determine_next_step(
        self, current_step: JourneyStep, response: Any, state: UserJourneyState
    ) -> str:
        """Détermine l'étape suivante basée sur la réponse et l'état"""

        # Logique spécifique par étape
        if current_step.id == "welcome":
            if isinstance(response, dict):
                choice = response.get("value", "")
                if choice == "quick":
                    return "destination_exploration"  # Skip profile discovery
                elif choice == "info":
                    return "journey_explanation"
                else:
                    return "profile_discovery"
            return "profile_discovery"

        elif current_step.id == "destination_exploration":
            if isinstance(response, dict):
                choice = response.get("value", "")
                return current_step.next_steps.get(choice, "destination_quiz")
            return "destination_quiz"

        # Logique générale
        for condition, next_step in current_step.next_steps.items():
            if condition == "any" or self._matches_condition(
                condition, response, state
            ):
                return next_step

        # Par défaut, retourne la première option
        return list(current_step.next_steps.values())[0]

    def _matches_condition(
        self, condition: str, response: Any, state: UserJourneyState
    ) -> bool:
        """Vérifie si une condition est remplie"""
        # Logique de correspondance des conditions
        if condition == "positive":
            if isinstance(response, dict):
                return response.get("value") in ["yes", "oui", "true"]
            return str(response).lower() in ["oui", "yes", "ok", "d'accord"]

        return condition in str(response).lower()

    def _get_personalized_content(
        self, user_id: str, step: JourneyStep
    ) -> Dict[str, Any]:
        """Génère du contenu personnalisé pour l'étape actuelle"""
        state = self.user_states[user_id]
        collected_data = state.collected_data

        personalized = {
            "dynamic_options": [],
            "personalized_tips": [],
            "context_message": "",
        }

        # Personnalisation basée sur les données collectées
        if step.id == "destination_quiz" and "traveler_type" in collected_data:
            traveler_type = collected_data["traveler_type"]

            if traveler_type == "aventurier":
                personalized["context_message"] = (
                    "Parfait pour un aventurier ! Cherchons des destinations avec des expériences uniques."
                )
                # Ajuster les options de climat pour favoriser les destinations d'aventure

            elif traveler_type == "culturel":
                personalized["context_message"] = (
                    "Excellent choix ! Trouvons des destinations riches en histoire et culture."
                )

        elif step.id == "budget_exploration" and "destination" in collected_data:
            dest = collected_data["destination"]
            personalized["context_message"] = f"Planifions votre budget pour {dest} !"
            # Ajuster les fourchettes de budget selon la destination

        return personalized

    def get_journey_summary(self, user_id: str) -> Dict[str, Any]:
        """Génère un résumé complet du parcours utilisateur"""
        if user_id not in self.user_states:
            return {}

        state = self.user_states[user_id]

        return {
            "user_profile": self._build_user_profile(state.collected_data),
            "journey_duration": (
                datetime.now() - state.journey_start_time
            ).total_seconds()
            / 60,
            "completion_rate": len(state.completed_steps) / len(self.journey_steps),
            "collected_preferences": state.collected_data,
            "stage_times": state.stage_completion_times,
            "personalization_level": self._calculate_personalization_score(
                state.collected_data
            ),
        }

    def _build_user_profile(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit un profil utilisateur à partir des données collectées"""
        profile = {
            "traveler_type": collected_data.get("traveler_type", "unknown"),
            "budget_range": collected_data.get("budget_amount", "medium"),
            "preferred_activities": collected_data.get("priority_activities", []),
            "accommodation_style": collected_data.get(
                "accommodation_preference", "hotel"
            ),
            "trip_duration": collected_data.get("trip_duration", "short"),
            "climate_preference": collected_data.get("preferred_climate", "temperate"),
        }

        return profile

    def _calculate_personalization_score(self, collected_data: Dict[str, Any]) -> float:
        """Calcule un score de personnalisation basé sur les données collectées"""
        total_possible_data_points = 15  # Nombre maximum de points de données
        collected_points = len([v for v in collected_data.values() if v])

        return (collected_points / total_possible_data_points) * 100

    def reset_journey(self, user_id: str):
        """Remet à zéro le parcours d'un utilisateur"""
        if user_id in self.user_states:
            del self.user_states[user_id]

    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Récupère les informations de progression d'un utilisateur"""
        if user_id not in self.user_states:
            return {"progress": 0, "current_stage": "not_started"}

        state = self.user_states[user_id]
        current_step = self.journey_steps[state.current_step]

        return {
            "progress": len(state.completed_steps) / len(self.journey_steps) * 100,
            "current_stage": current_step.stage.value,
            "current_step": current_step.title,
            "completed_stages": list(
                set(
                    [
                        self.journey_steps[step].stage.value
                        for step in state.completed_steps
                    ]
                )
            ),
            "estimated_time_remaining": self._estimate_remaining_time(state),
        }

    def _estimate_remaining_time(self, state: UserJourneyState) -> int:
        """Estime le temps restant en minutes"""
        remaining_steps = len(self.journey_steps) - len(state.completed_steps)
        avg_time_per_step = 2  # minutes
        return remaining_steps * avg_time_per_step
