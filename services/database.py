from pymongo import MongoClient
from datetime import datetime
import os
from typing import Dict, List, Optional, Any
from models.user_profile import UserProfile, UserPreferences, TravelPlan


class UserDatabase:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client.easy_travel
        self.users = self.db.users
        self.conversations = self.db.conversations
        self.travel_plans = self.db.travel_plans

        # Créer les index pour optimiser les requêtes
        self._create_indexes()

    def get_user_profile(self, user_id: str) -> dict:
        """Récupère le profil utilisateur"""
        return self.users.find_one({"user_id": user_id})

    def update_user_preferences(self, user_id: str, preferences: dict):
        """Met à jour les préférences utilisateur"""
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"preferences": preferences, "last_updated": datetime.now()}},
            upsert=True,
        )

    def save_conversation(self, user_id: str, user_message: str, bot_response: str):
        """Sauvegarde une interaction de conversation"""
        self.conversations.insert_one(
            {
                "user_id": user_id,
                "user_message": user_message,
                "bot_response": bot_response,
                "timestamp": datetime.now(),
            }
        )

    def save_travel_plan(self, user_id: str, plan: str):
        """Sauvegarde un plan de voyage généré"""
        self.travel_plans.insert_one(
            {"user_id": user_id, "plan": plan, "generated_at": datetime.now()}
        )

    def _create_indexes(self):
        """Crée les index pour optimiser les performances"""
        try:
            self.users.create_index("user_id", unique=True)
            self.conversations.create_index([("user_id", 1), ("timestamp", -1)])
            self.travel_plans.create_index([("user_id", 1), ("generated_at", -1)])
        except Exception as e:
            print(f"Erreur lors de la création des index: {e}")

    def create_or_update_user_profile(self, user_profile: UserProfile) -> bool:
        """Crée ou met à jour un profil utilisateur complet"""
        try:
            result = self.users.update_one(
                {"user_id": user_profile.user_id},
                {"$set": user_profile.to_dict()},
                upsert=True,
            )
            return result.acknowledged
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du profil: {e}")
            return False

    def get_user_profile_model(self, user_id: str) -> Optional[UserProfile]:
        """Récupère le profil utilisateur complet sous forme de modèle Pydantic"""
        try:
            user_data = self.users.find_one({"user_id": user_id})
            if user_data:
                return UserProfile.from_dict(user_data)
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du profil: {e}")
            return None

    def update_user_preferences_advanced(
        self, user_id: str, preferences: UserPreferences
    ) -> bool:
        """Met à jour les préférences utilisateur avec le modèle Pydantic"""
        try:
            result = self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "preferences": preferences.dict(),
                        "last_activity": datetime.now(),
                    },
                    "$inc": {"total_conversations": 1},
                },
                upsert=True,
            )
            return result.acknowledged
        except Exception as e:
            print(f"Erreur lors de la mise à jour des préférences: {e}")
            return False

    def save_travel_plan_model(self, travel_plan: TravelPlan) -> bool:
        """Sauvegarde un plan de voyage avec le modèle Pydantic"""
        try:
            result = self.travel_plans.insert_one(travel_plan.to_dict())

            # Met à jour le compteur de plans générés
            self.users.update_one(
                {"user_id": travel_plan.user_id}, {"$inc": {"plans_generated": 1}}
            )

            return result.acknowledged
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du plan: {e}")
            return False

    def get_user_travel_plans(self, user_id: str, limit: int = 10) -> List[TravelPlan]:
        """Récupère les plans de voyage d'un utilisateur"""
        try:
            plans_data = list(
                self.travel_plans.find({"user_id": user_id})
                .sort("generated_at", -1)
                .limit(limit)
            )

            plans = []
            for plan_data in plans_data:
                try:
                    plans.append(TravelPlan(**plan_data))
                except Exception as e:
                    print(f"Erreur lors de la conversion du plan: {e}")
                    continue

            return plans
        except Exception as e:
            print(f"Erreur lors de la récupération des plans: {e}")
            return []

    def get_conversation_history(
        self, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Récupère l'historique des conversations d'un utilisateur"""
        try:
            conversations = list(
                self.conversations.find({"user_id": user_id})
                .sort("timestamp", -1)
                .limit(limit)
            )

            return conversations
        except Exception as e:
            print(f"Erreur lors de la récupération de l'historique: {e}")
            return []

    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques d'un utilisateur"""
        try:
            user_profile = self.get_user_profile(user_id)
            if not user_profile:
                return {}

            conversation_count = self.conversations.count_documents(
                {"user_id": user_id}
            )
            plan_count = self.travel_plans.count_documents({"user_id": user_id})

            # Dernière activité
            last_conversation = self.conversations.find_one(
                {"user_id": user_id}, sort=[("timestamp", -1)]
            )

            return {
                "total_conversations": conversation_count,
                "total_plans": plan_count,
                "last_activity": (
                    last_conversation["timestamp"] if last_conversation else None
                ),
                "member_since": user_profile.get("created_at"),
                "preferences_set": bool(user_profile.get("preferences")),
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return {}

    def search_similar_users(
        self, user_preferences: UserPreferences, limit: int = 5
    ) -> List[str]:
        """Trouve des utilisateurs avec des préférences similaires"""
        try:
            # Requête MongoDB pour trouver des utilisateurs similaires
            pipeline = [
                {
                    "$match": {
                        "preferences.preferred_activities": {
                            "$in": user_preferences.preferred_activities
                        }
                    }
                },
                {"$limit": limit},
            ]

            similar_users = list(self.users.aggregate(pipeline))
            return [user["user_id"] for user in similar_users]

        except Exception as e:
            print(f"Erreur lors de la recherche d'utilisateurs similaires: {e}")
            return []
