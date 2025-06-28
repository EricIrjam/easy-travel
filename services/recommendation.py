from typing import List, Dict, Any, Optional
from models.user_profile import UserProfile, TravelType, BudgetRange
import json
import requests
import os


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
                },
                "rome": {
                    "climate": "mediterranean",
                    "budget": "medium",
                    "activities": ["culture", "histoire", "gastronomie"],
                },
                "barcelone": {
                    "climate": "mediterranean",
                    "budget": "medium",
                    "activities": ["plage", "culture", "architecture"],
                },
                "amsterdam": {
                    "climate": "oceanic",
                    "budget": "high",
                    "activities": ["culture", "vélo", "canaux"],
                },
                "prague": {
                    "climate": "continental",
                    "budget": "low",
                    "activities": ["culture", "architecture", "bière"],
                },
            },
            "asie": {
                "tokyo": {
                    "climate": "subtropical",
                    "budget": "high",
                    "activities": ["culture", "technologie", "gastronomie"],
                },
                "bangkok": {
                    "climate": "tropical",
                    "budget": "low",
                    "activities": ["culture", "temples", "street food"],
                },
                "singapour": {
                    "climate": "tropical",
                    "budget": "high",
                    "activities": ["modernité", "gastronomie", "shopping"],
                },
            },
            "amerique": {
                "new_york": {
                    "climate": "continental",
                    "budget": "high",
                    "activities": ["culture", "shopping", "musées"],
                },
                "buenos_aires": {
                    "climate": "subtropical",
                    "budget": "medium",
                    "activities": ["culture", "tango", "gastronomie"],
                },
            },
        }

    def get_personalized_recommendations(
        self, user_profile: UserProfile, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Génère des recommandations personnalisées basées sur le profil utilisateur"""
        preferences = user_profile.preferences
        recommendations = []

        # Score chaque destination
        for region, destinations in self.destinations_db.items():
            for dest_name, dest_info in destinations.items():
                score = self._calculate_destination_score(dest_info, preferences)

                if score > 0.3:  # Seuil minimum
                    recommendations.append(
                        {
                            "destination": dest_name.title(),
                            "region": region,
                            "score": round(score, 2),
                            "reason": self._generate_recommendation_reason(
                                dest_info, preferences
                            ),
                            "estimated_budget": self._estimate_budget(
                                dest_info["budget"], preferences.budget_range
                            ),
                            "best_activities": dest_info["activities"][:3],
                            "climate": dest_info["climate"],
                        }
                    )

        # Trie par score et retourne le top
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]

    def _calculate_destination_score(
        self, destination: Dict[str, Any], preferences
    ) -> float:
        """Calcule un score de compatibilité entre une destination et les préférences"""
        score = 0.0

        # Score basé sur les activités préférées
        dest_activities = set(destination["activities"])
        user_activities = set(preferences.preferred_activities)

        if user_activities:
            activity_match = len(dest_activities.intersection(user_activities)) / len(
                user_activities
            )
            score += activity_match * 0.4
        else:
            score += 0.2  # Score neutre si pas d'activités spécifiées

        # Score basé sur le budget
        if preferences.budget_range:
            budget_compatibility = self._calculate_budget_compatibility(
                destination["budget"], preferences.budget_range
            )
            score += budget_compatibility * 0.3
        else:
            score += 0.15  # Score neutre

        # Score basé sur le climat préféré
        if preferences.preferred_climate:
            if destination["climate"] == preferences.preferred_climate:
                score += 0.2
        else:
            score += 0.1  # Score neutre

        # Bonus pour les destinations déjà visitées (inverse)
        if destination in preferences.preferred_destinations:
            score += 0.1

        return min(score, 1.0)

    def _calculate_budget_compatibility(
        self, dest_budget: str, user_budget: BudgetRange
    ) -> float:
        """Calcule la compatibilité budgétaire"""
        budget_matrix = {
            ("low", BudgetRange.LOW): 1.0,
            ("low", BudgetRange.MEDIUM): 0.8,
            ("low", BudgetRange.HIGH): 0.6,
            ("low", BudgetRange.LUXURY): 0.4,
            ("medium", BudgetRange.LOW): 0.3,
            ("medium", BudgetRange.MEDIUM): 1.0,
            ("medium", BudgetRange.HIGH): 0.9,
            ("medium", BudgetRange.LUXURY): 0.7,
            ("high", BudgetRange.LOW): 0.1,
            ("high", BudgetRange.MEDIUM): 0.4,
            ("high", BudgetRange.HIGH): 1.0,
            ("high", BudgetRange.LUXURY): 0.9,
        }

        return budget_matrix.get((dest_budget, user_budget), 0.5)

    def _generate_recommendation_reason(
        self, destination: Dict[str, Any], preferences
    ) -> str:
        """Génère une raison personnalisée pour la recommandation"""
        reasons = []

        # Activités correspondantes
        dest_activities = set(destination["activities"])
        user_activities = set(preferences.preferred_activities)
        matching_activities = dest_activities.intersection(user_activities)

        if matching_activities:
            reasons.append(f"Parfait pour {', '.join(matching_activities)}")

        # Budget
        if preferences.budget_range:
            budget_texts = {
                BudgetRange.LOW: "budget économique",
                BudgetRange.MEDIUM: "budget modéré",
                BudgetRange.HIGH: "budget généreux",
                BudgetRange.LUXURY: "voyage de luxe",
            }
            reasons.append(f"Adapté à votre {budget_texts[preferences.budget_range]}")

        return " • ".join(reasons) if reasons else "Destination populaire et variée"

    def _estimate_budget(
        self, dest_budget_category: str, user_budget: Optional[BudgetRange]
    ) -> str:
        """Estime le budget pour la destination"""
        budget_estimates = {
            "low": "400-800€ pour 7 jours",
            "medium": "800-1500€ pour 7 jours",
            "high": "1500-2500€ pour 7 jours",
        }

        return budget_estimates.get(dest_budget_category, "Budget à définir")

    def get_activity_suggestions(
        self, destination: str, interests: List[str]
    ) -> List[Dict[str, Any]]:
        """Suggère des activités spécifiques pour une destination"""
        activity_suggestions = {
            "culture": ["Visites de musées", "Tours historiques", "Spectacles locaux"],
            "gastronomie": ["Tours culinaires", "Cours de cuisine", "Marchés locaux"],
            "nature": ["Randonnées", "Parcs nationaux", "Observation de la faune"],
            "plage": ["Sports nautiques", "Bronzage", "Restaurants de plage"],
            "aventure": ["Escalade", "Sports extrêmes", "Excursions"],
        }

        suggestions = []
        for interest in interests:
            if interest.lower() in activity_suggestions:
                for activity in activity_suggestions[interest.lower()]:
                    suggestions.append(
                        {
                            "activity": activity,
                            "category": interest,
                            "destination": destination,
                        }
                    )

        return suggestions

    def generate_itinerary(
        self, destination: str, duration_days: int, interests: List[str]
    ) -> List[Dict[str, Any]]:
        """Génère un itinéraire jour par jour"""
        daily_plan = []

        for day in range(1, duration_days + 1):
            activities = self.get_activity_suggestions(destination, interests)

            # Sélectionne 2-3 activités par jour
            day_activities = activities[: min(3, len(activities))]

            daily_plan.append(
                {
                    "day": day,
                    "morning": (
                        day_activities[0]
                        if len(day_activities) > 0
                        else {
                            "activity": "Explorer le centre-ville",
                            "category": "découverte",
                        }
                    ),
                    "afternoon": (
                        day_activities[1]
                        if len(day_activities) > 1
                        else {"activity": "Déjeuner local", "category": "gastronomie"}
                    ),
                    "evening": (
                        day_activities[2]
                        if len(day_activities) > 2
                        else {"activity": "Dîner et repos", "category": "détente"}
                    ),
                }
            )

        return daily_plan
