import requests
import os

class TravelAPI:
    def __init__(self):
        self.google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    def get_recommendations(self, destination: str) -> list:
        """Récupère des recommandations pour une destination"""
        # Intégration avec Google Places API
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"attractions touristiques {destination}",
            "key": self.google_maps_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            recommendations = []
            for place in data.get("results", [])[:5]:  # Top 5
                recommendations.append({
                    "name": place.get("name"),
                    "rating": place.get("rating"),
                    "address": place.get("formatted_address")
                })
            
            return recommendations
        except Exception as e:
            print(f"Erreur API: {e}")
            return []
    
    def get_weather_info(self, destination: str) -> dict:
        """Récupère les informations météo (à implémenter avec OpenWeatherMap)"""
        # À implémenter avec l'API OpenWeatherMap
        return {"status": "À implémenter"}