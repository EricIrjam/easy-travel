from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TravelType(str, Enum):
    LEISURE = "leisure"
    BUSINESS = "business"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    ROMANTIC = "romantic"
    FAMILY = "family"


class BudgetRange(str, Enum):
    LOW = "low"  # Moins de 500€
    MEDIUM = "medium"  # 500-1500€
    HIGH = "high"  # 1500-3000€
    LUXURY = "luxury"  # Plus de 3000€


class AccommodationType(str, Enum):
    HOTEL = "hotel"
    HOSTEL = "hostel"
    APARTMENT = "apartment"
    VILLA = "villa"
    RESORT = "resort"


class UserPreferences(BaseModel):
    # Informations de base
    preferred_destinations: List[str] = Field(default_factory=list)
    budget_range: Optional[BudgetRange] = None
    travel_type: Optional[TravelType] = None
    accommodation_type: Optional[AccommodationType] = None

    # Activités préférées
    preferred_activities: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)

    # Contraintes
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_requirements: List[str] = Field(default_factory=list)
    language_preferences: List[str] = Field(default_factory=list)

    # Préférences de voyage
    preferred_climate: Optional[str] = None
    group_size: Optional[int] = None
    max_flight_duration: Optional[int] = None  # en heures

    # Métadonnées
    last_updated: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None

    preferences: UserPreferences = Field(default_factory=UserPreferences)

    # Historique
    total_conversations: int = Field(default=0)
    plans_generated: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

    def update_activity(self):
        """Met à jour l'horodatage de la dernière activité"""
        self.last_activity = datetime.now()
        self.total_conversations += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le profil en dictionnaire pour MongoDB"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "country": self.country,
            "preferences": self.preferences.dict(),
            "total_conversations": self.total_conversations,
            "plans_generated": self.plans_generated,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Crée un UserProfile depuis un dictionnaire MongoDB"""
        if "preferences" in data:
            data["preferences"] = UserPreferences(**data["preferences"])
        return cls(**data)


class TravelPlan(BaseModel):
    user_id: str
    destination: str
    duration_days: int
    budget_estimated: float

    # Itinéraire
    daily_activities: List[Dict[str, Any]] = Field(default_factory=list)
    accommodations: List[Dict[str, Any]] = Field(default_factory=list)
    restaurants: List[Dict[str, Any]] = Field(default_factory=list)

    # Conseils
    practical_tips: List[str] = Field(default_factory=list)
    packing_list: List[str] = Field(default_factory=list)

    # Métadonnées
    generated_at: datetime = Field(default_factory=datetime.now)
    is_favorite: bool = Field(default=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le plan en dictionnaire pour MongoDB"""
        return {
            "user_id": self.user_id,
            "destination": self.destination,
            "duration_days": self.duration_days,
            "budget_estimated": self.budget_estimated,
            "daily_activities": self.daily_activities,
            "accommodations": self.accommodations,
            "restaurants": self.restaurants,
            "practical_tips": self.practical_tips,
            "packing_list": self.packing_list,
            "generated_at": self.generated_at,
            "is_favorite": self.is_favorite,
        }
