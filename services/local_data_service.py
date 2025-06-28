import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class LocalAttraction:
    name: str
    category: str
    description: str
    address: str
    rating: float
    price_level: int  # 1-4
    opening_hours: Dict[str, str]
    duration_visit: int  # en minutes
    best_time_visit: str
    accessibility: bool
    languages_available: List[str]
    booking_required: bool
    seasonal_info: Optional[str] = None


@dataclass
class LocalRestaurant:
    name: str
    cuisine_type: str
    description: str
    address: str
    rating: float
    price_range: str  # €, €€, €€€, €€€€
    specialties: List[str]
    opening_hours: Dict[str, str]
    reservation_required: bool
    dietary_options: List[str]  # vegetarian, vegan, gluten-free
    atmosphere: str
    local_favorite: bool


@dataclass
class LocalEvent:
    name: str
    category: str
    description: str
    start_date: str
    end_date: str
    location: str
    price: Optional[str]
    booking_url: Optional[str]
    target_audience: List[str]


@dataclass
class TransportInfo:
    type: str  # metro, bus, tram, taxi, walking
    description: str
    cost: str
    duration: str
    frequency: str
    accessibility: bool
    tips: List[str]


@dataclass
class CityInfo:
    name: str
    country: str
    timezone: str
    currency: str
    languages: List[str]
    emergency_numbers: Dict[str, str]
    tipping_culture: str
    cultural_etiquette: List[str]
    safety_tips: List[str]
    public_holidays: List[Dict[str, str]] = None


class LocalDataService:
    def __init__(self):
        self.data_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "local_data"
        )
        self._ensure_data_directory()
        self._initialize_data()

    def _ensure_data_directory(self):
        """Crée le répertoire de données s'il n'existe pas"""
        os.makedirs(self.data_path, exist_ok=True)

    def _initialize_data(self):
        """Initialise les données locales pour les principales destinations"""

        # Données Paris
        paris_data = {
            "city_info": {
                "name": "Paris",
                "country": "France",
                "timezone": "Europe/Paris",
                "currency": "EUR",
                "languages": ["Français", "Anglais"],
                "emergency_numbers": {"Police": "17", "Pompiers": "18", "SAMU": "15"},
                "tipping_culture": "Service compris, 5-10% si satisfait",
                "public_holidays": [
                    {"date": "2025-07-14", "name": "Fête Nationale"},
                    {"date": "2025-08-15", "name": "Assomption"},
                    {"date": "2025-12-25", "name": "Noël"},
                ],
                "cultural_etiquette": [
                    "Dire 'Bonjour' en entrant dans un commerce",
                    "Vouvoyer les inconnus",
                    "Ne pas manger en marchant dans la rue",
                    "Respecter les horaires de repas",
                ],
                "safety_tips": [
                    "Attention aux pickpockets dans le métro",
                    "Éviter certains quartiers la nuit",
                    "Garder ses affaires près de soi en terrasse",
                ],
            },
            "attractions": [
                {
                    "name": "Musée du Louvre",
                    "category": "Musée",
                    "description": "Le plus grand musée du monde avec la Joconde",
                    "address": "Rue de Rivoli, 75001 Paris",
                    "rating": 4.6,
                    "price_level": 3,
                    "opening_hours": {
                        "lundi": "Fermé",
                        "mardi": "09:00-18:00",
                        "mercredi": "09:00-21:45",
                        "jeudi": "09:00-18:00",
                        "vendredi": "09:00-21:45",
                        "samedi": "09:00-18:00",
                        "dimanche": "09:00-18:00",
                    },
                    "duration_visit": 180,
                    "best_time_visit": "Matin ou en soirée",
                    "accessibility": True,
                    "languages_available": [
                        "Français",
                        "Anglais",
                        "Espagnol",
                        "Italien",
                    ],
                    "booking_required": True,
                    "seasonal_info": "Très fréquenté en été",
                },
                {
                    "name": "Tour Eiffel",
                    "category": "Monument",
                    "description": "Symbole emblématique de Paris",
                    "address": "Champ de Mars, 75007 Paris",
                    "rating": 4.4,
                    "price_level": 2,
                    "opening_hours": {
                        "lundi": "09:30-23:45",
                        "mardi": "09:30-23:45",
                        "mercredi": "09:30-23:45",
                        "jeudi": "09:30-23:45",
                        "vendredi": "09:30-23:45",
                        "samedi": "09:30-23:45",
                        "dimanche": "09:30-23:45",
                    },
                    "duration_visit": 120,
                    "best_time_visit": "Coucher de soleil",
                    "accessibility": False,
                    "languages_available": ["Français", "Anglais"],
                    "booking_required": True,
                    "seasonal_info": "Magnifique illuminée en hiver",
                },
            ],
            "restaurants": [
                {
                    "name": "L'As du Fallafel",
                    "cuisine_type": "Moyen-Oriental",
                    "description": "Meilleur falafel du Marais",
                    "address": "34 Rue des Rosiers, 75004 Paris",
                    "rating": 4.3,
                    "price_range": "€€",
                    "specialties": ["Falafel", "Shawarma", "Houmous"],
                    "opening_hours": {
                        "lundi": "12:00-24:00",
                        "mardi": "12:00-24:00",
                        "mercredi": "12:00-24:00",
                        "jeudi": "12:00-24:00",
                        "vendredi": "Fermé",
                        "samedi": "Fermé",
                        "dimanche": "12:00-24:00",
                    },
                    "reservation_required": False,
                    "dietary_options": ["vegetarian", "vegan"],
                    "atmosphere": "Décontracté, authentique",
                    "local_favorite": True,
                }
            ],
            "transport": [
                {
                    "type": "Metro",
                    "description": "Réseau métropolitain dense",
                    "cost": "2.15€ le ticket",
                    "duration": "Rapide dans Paris",
                    "frequency": "2-4 minutes aux heures de pointe",
                    "accessibility": "Variable selon les stations",
                    "tips": [
                        "Achetez un passe journalier si vous voyagez beaucoup",
                        "Évitez les heures de pointe (8h-9h, 18h-19h)",
                        "Attention à la fermeture vers 1h15",
                    ],
                }
            ],
            "events": [
                {
                    "name": "Nuit Blanche",
                    "category": "Art",
                    "description": "Nuit d'art contemporain gratuite",
                    "start_date": "2025-10-04",
                    "end_date": "2025-10-05",
                    "location": "Toute la ville",
                    "price": "Gratuit",
                    "booking_url": None,
                    "target_audience": ["Art", "Culture", "Jeunes"],
                }
            ],
        }

        # Sauvegarde les données Paris
        self._save_city_data("paris", paris_data)

        # Données Rome (exemple abrégé)
        rome_data = {
            "city_info": {
                "name": "Rome",
                "country": "Italie",
                "timezone": "Europe/Rome",
                "currency": "EUR",
                "languages": ["Italien", "Anglais"],
                "emergency_numbers": {"Police": "112", "Pompiers": "115"},
                "tipping_culture": "10-15% dans les restaurants",
                "cultural_etiquette": [
                    "S'habiller correctement dans les églises",
                    "Pas de short dans les sites religieux",
                    "Respect des sites archéologiques",
                ],
                "safety_tips": [
                    "Attention aux pickpockets près du Colisée",
                    "Éviter les vendeurs ambulants",
                ],
            },
            "attractions": [
                {
                    "name": "Colisée",
                    "category": "Monument historique",
                    "description": "Amphithéâtre antique emblématique",
                    "address": "Piazza del Colosseo, 1, 00184 Roma",
                    "rating": 4.7,
                    "price_level": 3,
                    "opening_hours": {
                        "lundi": "08:30-16:30",
                        "mardi": "08:30-16:30",
                        "mercredi": "08:30-16:30",
                        "jeudi": "08:30-16:30",
                        "vendredi": "08:30-16:30",
                        "samedi": "08:30-16:30",
                        "dimanche": "08:30-16:30",
                    },
                    "duration_visit": 150,
                    "best_time_visit": "Tôt le matin",
                    "accessibility": True,
                    "languages_available": ["Italien", "Anglais", "Français"],
                    "booking_required": True,
                    "seasonal_info": "Très chaud en été, protection solaire nécessaire",
                }
            ],
        }

        self._save_city_data("rome", rome_data)

    def _save_city_data(self, city: str, data: Dict[str, Any]):
        """Sauvegarde les données d'une ville"""
        file_path = os.path.join(self.data_path, f"{city.lower()}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_city_data(self, city: str) -> Optional[Dict[str, Any]]:
        """Charge les données d'une ville"""
        file_path = os.path.join(self.data_path, f"{city.lower()}.json")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def get_city_info(self, city: str) -> Optional[CityInfo]:
        """Récupère les informations générales d'une ville"""
        data = self._load_city_data(city)
        if data and "city_info" in data:
            info = data["city_info"]
            return CityInfo(**info)
        return None

    def get_local_attractions(
        self, city: str, category: Optional[str] = None
    ) -> List[LocalAttraction]:
        """Récupère les attractions locales d'une ville"""
        data = self._load_city_data(city)
        attractions = []

        if data and "attractions" in data:
            for attr_data in data["attractions"]:
                if (
                    category is None
                    or attr_data.get("category", "").lower() == category.lower()
                ):
                    attractions.append(LocalAttraction(**attr_data))

        return attractions

    def get_local_restaurants(
        self, city: str, cuisine_type: Optional[str] = None
    ) -> List[LocalRestaurant]:
        """Récupère les restaurants locaux d'une ville"""
        data = self._load_city_data(city)
        restaurants = []

        if data and "restaurants" in data:
            for rest_data in data["restaurants"]:
                if (
                    cuisine_type is None
                    or rest_data.get("cuisine_type", "").lower() == cuisine_type.lower()
                ):
                    restaurants.append(LocalRestaurant(**rest_data))

        return restaurants

    def get_transport_info(self, city: str) -> List[TransportInfo]:
        """Récupère les informations de transport d'une ville"""
        data = self._load_city_data(city)
        transport_list = []

        if data and "transport" in data:
            for trans_data in data["transport"]:
                transport_list.append(TransportInfo(**trans_data))

        return transport_list

    def get_local_events(
        self, city: str, date_range: Optional[tuple] = None
    ) -> List[LocalEvent]:
        """Récupère les événements locaux d'une ville"""
        data = self._load_city_data(city)
        events = []

        if data and "events" in data:
            for event_data in data["events"]:
                event = LocalEvent(**event_data)

                # Filtre par date si spécifié
                if date_range:
                    event_date = datetime.strptime(event.start_date, "%Y-%m-%d").date()
                    if date_range[0] <= event_date <= date_range[1]:
                        events.append(event)
                else:
                    events.append(event)

        return events

    def get_personalized_recommendations(
        self, city: str, user_preferences: Dict[str, Any]
    ) -> Dict[str, List[Any]]:
        """Récupère des recommandations personnalisées basées sur les préférences utilisateur"""
        recommendations = {
            "attractions": [],
            "restaurants": [],
            "events": [],
            "tips": [],
        }

        # Recommandations d'attractions basées sur les activités préférées
        activities = user_preferences.get("preferred_activities", [])
        all_attractions = self.get_local_attractions(city)

        for attraction in all_attractions:
            score = 0
            if "culture" in activities and attraction.category.lower() in [
                "musée",
                "monument",
                "art",
            ]:
                score += 3
            if (
                "histoire" in activities
                and "historique" in attraction.description.lower()
            ):
                score += 2

            if score > 0:
                recommendations["attractions"].append((attraction, score))

        # Trie par score
        recommendations["attractions"] = [
            item[0]
            for item in sorted(
                recommendations["attractions"], key=lambda x: x[1], reverse=True
            )
        ]

        # Recommandations de restaurants
        budget = user_preferences.get("budget_range", "medium")
        restaurants = self.get_local_restaurants(city)

        for restaurant in restaurants:
            if budget == "low" and restaurant.price_range in ["€", "€€"]:
                recommendations["restaurants"].append(restaurant)
            elif budget == "medium" and restaurant.price_range in ["€€", "€€€"]:
                recommendations["restaurants"].append(restaurant)
            elif budget in ["high", "luxury"] and restaurant.price_range in [
                "€€€",
                "€€€€",
            ]:
                recommendations["restaurants"].append(restaurant)

        # Conseils personnalisés
        city_info = self.get_city_info(city)
        if city_info:
            recommendations["tips"] = (
                city_info.safety_tips + city_info.cultural_etiquette
            )

        return recommendations

    def add_user_review(
        self, city: str, place_name: str, rating: float, comment: str, user_id: str
    ):
        """Ajoute un avis utilisateur (à implémenter avec MongoDB)"""
        # Cette fonction pourrait être intégrée avec MongoDB pour stocker les avis
        pass
