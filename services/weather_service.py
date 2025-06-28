import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
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


@dataclass
class WeatherForecast:
    date: str
    temp_min: float
    temp_max: float
    description: str
    precipitation_chance: int
    wind_speed: float


class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def get_current_weather(
        self, city: str, country_code: str = ""
    ) -> Optional[WeatherInfo]:
        """Récupère la météo actuelle pour une ville"""
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
                    visibility=data.get("visibility", 0) / 1000,  # Convertir en km
                    sunrise=datetime.fromtimestamp(data["sys"]["sunrise"]).strftime(
                        "%H:%M"
                    ),
                    sunset=datetime.fromtimestamp(data["sys"]["sunset"]).strftime(
                        "%H:%M"
                    ),
                )
        except Exception as e:
            print(f"Erreur météo pour {city}: {e}")
            return self._get_mock_weather(city)

    def get_forecast(self, city: str, days: int = 5) -> List[WeatherForecast]:
        """Récupère les prévisions météo sur plusieurs jours"""
        try:
            url = f"{self.base_url}/forecast"
            params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "fr"}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                forecasts = []

                # Groupe par jour
                daily_data = {}
                for item in data["list"][
                    : days * 8
                ]:  # 8 prévisions par jour (toutes les 3h)
                    date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")

                    if date not in daily_data:
                        daily_data[date] = []

                    daily_data[date].append(item)

                # Crée un résumé par jour
                for date, day_items in daily_data.items():
                    temps = [item["main"]["temp"] for item in day_items]

                    forecast = WeatherForecast(
                        date=datetime.strptime(date, "%Y-%m-%d").strftime("%A %d/%m"),
                        temp_min=min(temps),
                        temp_max=max(temps),
                        description=day_items[len(day_items) // 2]["weather"][0][
                            "description"
                        ],
                        precipitation_chance=day_items[0].get("pop", 0) * 100,
                        wind_speed=day_items[0]["wind"]["speed"],
                    )
                    forecasts.append(forecast)

                return forecasts[:days]

        except Exception as e:
            print(f"Erreur prévisions pour {city}: {e}")
            return self._get_mock_forecast(city, days)

    def _get_mock_weather(self, city: str) -> WeatherInfo:
        """Données météo simulées si l'API ne fonctionne pas"""
        mock_data = {
            "paris": WeatherInfo(
                18.5, 65, "Nuageux", 20.1, 3.2, 8.5, sunrise="07:30", sunset="20:45"
            ),
            "rome": WeatherInfo(
                24.3, 45, "Ensoleillé", 26.1, 2.1, 12.0, sunrise="06:45", sunset="21:15"
            ),
            "tokyo": WeatherInfo(
                22.1,
                70,
                "Partiellement nuageux",
                24.5,
                1.8,
                9.2,
                sunrise="05:30",
                sunset="19:00",
            ),
            "barcelone": WeatherInfo(
                21.8, 55, "Ensoleillé", 23.2, 2.8, 11.5, sunrise="07:00", sunset="20:30"
            ),
        }

        return mock_data.get(
            city.lower(), WeatherInfo(20.0, 60, "Temps variable", 21.0, 2.5, 10.0)
        )

    def _get_mock_forecast(self, city: str, days: int) -> List[WeatherForecast]:
        """Prévisions simulées"""
        forecasts = []
        base_date = datetime.now()

        for i in range(days):
            date = (base_date + timedelta(days=i)).strftime("%A %d/%m")
            forecasts.append(
                WeatherForecast(
                    date=date,
                    temp_min=15 + i,
                    temp_max=25 + i,
                    description="Variable",
                    precipitation_chance=20 + (i * 10),
                    wind_speed=2.5,
                )
            )

        return forecasts

    def get_travel_weather_advice(
        self, weather: WeatherInfo, activities: List[str]
    ) -> List[str]:
        """Génère des conseils météo pour les activités"""
        advice = []

        if weather.temperature < 10:
            advice.append("🧥 Pensez à emporter des vêtements chauds")
        elif weather.temperature > 30:
            advice.append("🌞 Température élevée, hydratez-vous bien")

        if weather.humidity > 80:
            advice.append("💧 Forte humidité, vêtements respirants recommandés")

        if weather.wind_speed > 5:
            advice.append("💨 Vent fort, attention aux activités extérieures")

        # Conseils spécifiques aux activités
        if "plage" in activities and weather.temperature < 20:
            advice.append("🏖️ Température fraîche pour la plage, pensez à un coupe-vent")

        if "nature" in activities and weather.description in ["pluie", "orage"]:
            advice.append("🌧️ Météo défavorable pour les activités nature")

        if "culture" in activities and weather.description in ["pluie", "orage"]:
            advice.append("🏛️ Parfait pour visiter les musées à l'abri")

        return advice if advice else ["☀️ Conditions météo favorables pour votre voyage"]
