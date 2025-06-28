import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from models.user_profile import BudgetRange, TravelType


class TravelHelpers:

    @staticmethod
    def extract_budget_from_text(text: str) -> Optional[str]:
        """Extrait un budget mentionné dans le texte"""
        # Patterns pour détecter les montants
        patterns = [
            r"(\d+)\s*(?:€|euros?|eur)",
            r"€\s*(\d+)",
            r"(\d+)\s*(?:dollars?|usd|\$)",
            r"\$\s*(\d+)",
            r"(?:budget|prix|coût).*?(\d+)",
            r"(\d+).*?(?:budget|prix|coût)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount = int(match.group(1))
                return f"{amount}€"

        # Détection de termes qualitatifs
        if any(
            term in text.lower() for term in ["pas cher", "économique", "petit budget"]
        ):
            return "Budget économique"
        elif any(term in text.lower() for term in ["moyen", "modéré", "raisonnable"]):
            return "Budget modéré"
        elif any(term in text.lower() for term in ["élevé", "important", "généreux"]):
            return "Budget élevé"
        elif any(term in text.lower() for term in ["luxe", "haut de gamme", "premium"]):
            return "Budget luxe"

        return None

    @staticmethod
    def extract_destinations_from_text(text: str) -> List[str]:
        """Extrait les destinations mentionnées dans le texte"""
        # Liste des destinations communes
        destinations = [
            "paris",
            "london",
            "tokyo",
            "new york",
            "rome",
            "barcelone",
            "madrid",
            "amsterdam",
            "berlin",
            "prague",
            "vienne",
            "budapest",
            "istanbul",
            "bangkok",
            "singapour",
            "hong kong",
            "sydney",
            "melbourne",
            "los angeles",
            "san francisco",
            "miami",
            "las vegas",
            "maroc",
            "egypte",
            "tunisie",
            "grece",
            "italie",
            "espagne",
            "portugal",
            "allemagne",
            "autriche",
            "suisse",
            "norvege",
            "japon",
            "coree",
            "chine",
            "inde",
            "indonesie",
            "vietnam",
            "bresil",
            "argentine",
            "mexique",
            "canada",
            "australie",
        ]

        text_lower = text.lower()
        found_destinations = []

        for dest in destinations:
            if dest in text_lower:
                found_destinations.append(dest.title())

        return found_destinations

    @staticmethod
    def extract_dates_from_text(text: str) -> Dict[str, Any]:
        """Extrait les informations de dates du texte"""
        date_info = {}

        # Mois en français
        months = {
            "janvier": 1,
            "février": 2,
            "mars": 3,
            "avril": 4,
            "mai": 5,
            "juin": 6,
            "juillet": 7,
            "août": 8,
            "septembre": 9,
            "octobre": 10,
            "novembre": 11,
            "décembre": 12,
        }

        # Détection de mois
        for month_name, month_num in months.items():
            if month_name in text.lower():
                date_info["month"] = month_name
                date_info["month_num"] = month_num
                break

        # Détection de saisons
        seasons = {
            "printemps": ["mars", "avril", "mai"],
            "été": ["juin", "juillet", "août"],
            "automne": ["septembre", "octobre", "novembre"],
            "hiver": ["décembre", "janvier", "février"],
        }

        for season, season_months in seasons.items():
            if season in text.lower():
                date_info["season"] = season
                date_info["season_months"] = season_months
                break

        # Détection de durée
        duration_patterns = [
            r"(\d+)\s*(?:jours?|day)",
            r"(\d+)\s*(?:semaines?|week)",
            r"(\d+)\s*(?:mois|month)",
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text.lower())
            if match:
                number = int(match.group(1))
                if "jour" in pattern or "day" in pattern:
                    date_info["duration_days"] = number
                elif "semaine" in pattern or "week" in pattern:
                    date_info["duration_days"] = number * 7
                elif "mois" in pattern or "month" in pattern:
                    date_info["duration_days"] = number * 30
                break

        return date_info

    @staticmethod
    def extract_activities_from_text(text: str) -> List[str]:
        """Extrait les activités mentionnées dans le texte"""
        activity_keywords = {
            "culture": [
                "musée",
                "monument",
                "histoire",
                "art",
                "culture",
                "patrimoine",
            ],
            "gastronomie": [
                "restaurant",
                "cuisine",
                "gastronomie",
                "manger",
                "spécialité",
            ],
            "nature": ["nature", "randonnée", "montagne", "forêt", "parc", "paysage"],
            "plage": ["plage", "mer", "océan", "soleil", "bronzer", "baignade"],
            "sport": ["sport", "vélo", "escalade", "ski", "surf", "fitness"],
            "shopping": ["shopping", "boutique", "marché", "achats", "souvenir"],
            "nightlife": ["nuit", "bar", "club", "sortie", "fête", "nightlife"],
            "détente": ["spa", "massage", "relax", "détente", "repos", "zen"],
        }

        mentioned_activities = []
        text_lower = text.lower()

        for activity, keywords in activity_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    mentioned_activities.append(activity)
                    break

        return list(set(mentioned_activities))  # Supprime les doublons

    @staticmethod
    def categorize_budget(budget_text: str) -> Optional[BudgetRange]:
        """Catégorise un budget textuel"""
        if not budget_text:
            return None

        budget_lower = budget_text.lower()

        # Extraction numérique
        amount_match = re.search(r"(\d+)", budget_text)
        if amount_match:
            amount = int(amount_match.group(1))
            if amount < 500:
                return BudgetRange.LOW
            elif amount < 1500:
                return BudgetRange.MEDIUM
            elif amount < 3000:
                return BudgetRange.HIGH
            else:
                return BudgetRange.LUXURY

        # Catégorisation qualitative
        if any(term in budget_lower for term in ["économique", "pas cher", "petit"]):
            return BudgetRange.LOW
        elif any(term in budget_lower for term in ["modéré", "moyen", "raisonnable"]):
            return BudgetRange.MEDIUM
        elif any(term in budget_lower for term in ["élevé", "important", "généreux"]):
            return BudgetRange.HIGH
        elif any(term in budget_lower for term in ["luxe", "premium", "haut de gamme"]):
            return BudgetRange.LUXURY

        return None

    @staticmethod
    def determine_travel_type(text: str, activities: List[str]) -> Optional[TravelType]:
        """Détermine le type de voyage basé sur le texte et les activités"""
        text_lower = text.lower()

        # Mots-clés par type de voyage
        type_keywords = {
            TravelType.BUSINESS: [
                "travail",
                "business",
                "professionnel",
                "conférence",
                "meeting",
            ],
            TravelType.ROMANTIC: [
                "romantique",
                "amoureux",
                "couple",
                "lune de miel",
                "anniversaire",
            ],
            TravelType.FAMILY: [
                "famille",
                "enfants",
                "parents",
                "grands-parents",
                "familial",
            ],
            TravelType.ADVENTURE: [
                "aventure",
                "extrême",
                "adrenaline",
                "escalade",
                "safari",
            ],
            TravelType.CULTURAL: [
                "culture",
                "histoire",
                "musée",
                "patrimoine",
                "découverte",
            ],
            TravelType.LEISURE: ["vacances", "détente", "repos", "loisir", "plaisir"],
        }

        # Score par type
        type_scores = {}

        for travel_type, keywords in type_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1

            # Bonus basé sur les activités
            if travel_type == TravelType.CULTURAL and "culture" in activities:
                score += 2
            elif travel_type == TravelType.ADVENTURE and "sport" in activities:
                score += 2
            elif travel_type == TravelType.LEISURE and "détente" in activities:
                score += 2

            type_scores[travel_type] = score

        # Retourne le type avec le score le plus élevé
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            return best_type[0] if best_type[1] > 0 else TravelType.LEISURE

        return TravelType.LEISURE  # Par défaut

    @staticmethod
    def format_preferences_for_display(preferences: Dict[str, Any]) -> str:
        """Formate les préférences pour un affichage lisible"""
        formatted_parts = []

        if "destination" in preferences:
            formatted_parts.append(f"🌍 Destination: {preferences['destination']}")

        if "budget" in preferences:
            formatted_parts.append(f"💰 Budget: {preferences['budget']}")

        if "preferred_activities" in preferences:
            activities = ", ".join(preferences["preferred_activities"])
            formatted_parts.append(f"🎯 Activités: {activities}")

        if "duration_days" in preferences:
            formatted_parts.append(f"📅 Durée: {preferences['duration_days']} jours")

        if "travel_type" in preferences:
            formatted_parts.append(f"✈️ Type: {preferences['travel_type']}")

        return (
            "\n".join(formatted_parts)
            if formatted_parts
            else "Aucune préférence collectée"
        )

    @staticmethod
    def generate_travel_tips(destination: str, activities: List[str]) -> List[str]:
        """Génère des conseils de voyage personnalisés"""
        tips = [
            f"Vérifiez les conditions météo pour {destination} avant votre départ",
            "Pensez à vérifier les exigences de visa si nécessaire",
            "Souscrivez une assurance voyage adaptée à vos activités",
        ]

        # Conseils spécifiques aux activités
        if "nature" in activities:
            tips.append("Emportez des chaussures de randonnée confortables")
            tips.append("N'oubliez pas la crème solaire et un chapeau")

        if "culture" in activities:
            tips.append("Renseignez-vous sur les horaires d'ouverture des musées")
            tips.append("Certains sites culturels offrent des réductions étudiants")

        if "plage" in activities:
            tips.append("Vérifiez la qualité de l'eau et les conditions de baignade")
            tips.append("Emportez des lunettes de soleil et de la crème waterproof")

        return tips
