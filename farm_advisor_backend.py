#!/usr/bin/env python3
"""
Core RootSense farm-advisor services.

This module keeps the reusable data and decision logic separate from the CLI,
GUI, and Flask API entrypoints.
"""

from __future__ import annotations

import os
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is listed, fallback is harmless.
    load_dotenv = None


if load_dotenv:
    load_dotenv()


DEFAULT_LATITUDE = 40.4167
DEFAULT_LONGITUDE = -87.3573
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)
WEATHER_USER_AGENT = "RootSense Farm Advisor (educational project)"


class WeatherService:
    """Fetches forecast and alert data from the weather.gov API."""

    def __init__(self, latitude: float, longitude: float):
        self.lat = latitude
        self.lon = longitude
        self.base_url = "https://api.weather.gov"
        self.headers = {"User-Agent": WEATHER_USER_AGENT}

    def get_forecast(self) -> Optional[List[Dict[str, Any]]]:
        """Return up to seven forecast periods for the configured location."""
        try:
            point_url = f"{self.base_url}/points/{self.lat},{self.lon}"
            response = requests.get(point_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            forecast_url = response.json()["properties"]["forecast"]
            forecast_response = requests.get(
                forecast_url, headers=self.headers, timeout=10
            )
            forecast_response.raise_for_status()
            return forecast_response.json()["properties"]["periods"][:7]
        except requests.RequestException as exc:
            print(f"Weather forecast request failed: {exc}")
            return None
        except (KeyError, TypeError) as exc:
            print(f"Weather forecast response was unexpected: {exc}")
            return None

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Return active weather alerts for the configured location."""
        try:
            alerts_url = f"{self.base_url}/alerts/active?point={self.lat},{self.lon}"
            response = requests.get(alerts_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get("features", [])
        except requests.RequestException as exc:
            print(f"Weather alerts request failed: {exc}")
            return []
        except (KeyError, TypeError) as exc:
            print(f"Weather alerts response was unexpected: {exc}")
            return []


class SensorData:
    """Provides demo sensor readings and field-condition interpretation."""

    @staticmethod
    def get_current_readings() -> Dict[str, Any]:
        """Return simulated RootSense readings for the demo application."""
        distance_cm = random.uniform(10, 80)
        return {
            "distance_cm": distance_cm,
            "temperature_c": random.uniform(18, 35),
            "ponding_detected": distance_cm < 15,
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def assess_conditions(readings: Dict[str, Any]) -> List[str]:
        """Classify field conditions from a sensor reading payload."""
        conditions: List[str] = []

        if readings["distance_cm"] < 15:
            conditions.append("CRITICAL: standing water detected")
        elif readings["distance_cm"] < 40:
            conditions.append("WARNING: elevated soil moisture")
        else:
            conditions.append("NORMAL: good drainage conditions")

        if readings["temperature_c"] > 32:
            conditions.append("High temperature may increase evaporation")
        elif readings["temperature_c"] < 20:
            conditions.append("Cool temperature may slow evaporation")

        return conditions


class GeminiAdvisor:
    """Uses Gemini to produce concise, context-aware agronomic advice."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = os.getenv("GEMINI_API_KEY") if api_key is None else api_key
        self.api_url = GEMINI_API_URL

    def get_advice(
        self,
        weather_data: Optional[List[Dict[str, Any]]],
        sensor_data: Dict[str, Any],
        farmer_question: str,
    ) -> str:
        """Return AI-generated advice, or a configuration message if disabled."""
        if not farmer_question.strip():
            return "Please provide a question for the farm advisor."

        if not self.api_key:
            return (
                "Gemini API key is not configured. Set GEMINI_API_KEY in your "
                "environment or local .env file to enable farm-advisor responses."
            )

        prompt = self._build_prompt(weather_data, sensor_data, farmer_question)
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except requests.RequestException as exc:
            return f"AI advice request failed: {exc}"
        except (KeyError, IndexError, TypeError) as exc:
            return f"AI advice response was unexpected: {exc}"

    def _build_prompt(
        self,
        weather_data: Optional[List[Dict[str, Any]]],
        sensor_data: Dict[str, Any],
        farmer_question: str,
    ) -> str:
        context = self._prepare_context(weather_data, sensor_data)
        return f"""You are an agricultural advisor helping farmers make practical field decisions.

Current field conditions:
{context}

Farmer question: {farmer_question}

Provide specific, actionable advice based on weather forecast and field sensor data.
Focus on runoff risk, planting or harvesting timing, irrigation needs, soil management,
and preventive measures. Keep the response concise and practical."""

    def _prepare_context(
        self,
        weather_data: Optional[List[Dict[str, Any]]],
        sensor_data: Dict[str, Any],
    ) -> str:
        lines = [
            "Field sensors:",
            f"  - Distance to surface: {sensor_data['distance_cm']:.1f} cm",
            f"  - Temperature: {sensor_data['temperature_c']:.1f} C",
            f"  - Ponding: {'yes' if sensor_data['ponding_detected'] else 'no'}",
            "  - Assessment: "
            + ", ".join(SensorData.assess_conditions(sensor_data)),
            "",
        ]

        if weather_data:
            lines.append("Weather forecast:")
            for period in weather_data:
                precip = (
                    period.get("probabilityOfPrecipitation", {}).get("value", 0)
                    or 0
                )
                lines.append(
                    f"  - {period['name']}: {period['shortForecast']}, "
                    f"{period['temperature']} {period['temperatureUnit']}, "
                    f"{precip}% precipitation"
                )

        return "\n".join(lines)


class FarmAdvisorAPI:
    """High-level service facade for dashboards, APIs, and scripts."""

    def __init__(
        self,
        latitude: float = DEFAULT_LATITUDE,
        longitude: float = DEFAULT_LONGITUDE,
        gemini_api_key: Optional[str] = None,
    ):
        self.lat = latitude
        self.lon = longitude
        self.weather_service = WeatherService(latitude, longitude)
        self.gemini_advisor = GeminiAdvisor(gemini_api_key)

    def get_all_data(self) -> Dict[str, Any]:
        """Return sensor, weather, alert, and runoff-risk data in one payload."""
        sensor_data = self.get_sensor_data()
        forecast = self.get_weather_forecast()
        alerts = self.get_weather_alerts()

        return {
            "sensor": sensor_data,
            "weather": forecast,
            "alerts": alerts,
            "risk": self.calculate_runoff_risk(forecast, sensor_data),
            "timestamp": datetime.now().isoformat(),
        }

    def get_sensor_data(self) -> Dict[str, Any]:
        return SensorData.get_current_readings()

    def get_weather_forecast(self) -> Optional[List[Dict[str, Any]]]:
        return self.weather_service.get_forecast()

    def get_weather_alerts(self) -> List[Dict[str, Any]]:
        return self.weather_service.get_alerts()

    def calculate_runoff_risk(
        self,
        forecast: Optional[List[Dict[str, Any]]] = None,
        sensor_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Score runoff risk from sensor data and near-term precipitation chance."""
        forecast = forecast if forecast is not None else self.get_weather_forecast()
        sensor_data = sensor_data if sensor_data is not None else self.get_sensor_data()

        risk_score = 0
        risk_factors: List[str] = []

        if sensor_data["distance_cm"] < 15:
            risk_score += 3
            risk_factors.append("Standing water already present")
        elif sensor_data["distance_cm"] < 40:
            risk_score += 2
            risk_factors.append("Elevated soil moisture")

        if forecast:
            total_precip = 0
            for period in forecast[:3]:
                precip = (
                    period.get("probabilityOfPrecipitation", {}).get("value", 0)
                    or 0
                )
                total_precip += precip
                if precip > 60:
                    risk_score += 2
                    risk_factors.append(f"High precipitation forecast: {precip}%")

            if total_precip > 100:
                risk_score += 1
                risk_factors.append("Multiple rain periods expected")

        if sensor_data["temperature_c"] < 5:
            risk_score += 1
            risk_factors.append("Cold temperatures reduce infiltration")

        if risk_score >= 5:
            level = "HIGH"
            indicator = "red"
            recommendation = (
                "Clear drainage paths and avoid field work until conditions improve."
            )
        elif risk_score >= 3:
            level = "MODERATE"
            indicator = "yellow"
            recommendation = "Monitor conditions closely and prepare drainage systems."
        else:
            level = "LOW"
            indicator = "green"
            recommendation = "Continue normal operations and routine monitoring."

        return {
            "score": min(risk_score, 10),
            "level": level,
            "indicator": indicator,
            "factors": risk_factors,
            "recommendation": recommendation,
        }

    def ask_ai_advisor(self, question: str) -> str:
        forecast = self.get_weather_forecast()
        sensor_data = self.get_sensor_data()
        return self.gemini_advisor.get_advice(forecast, sensor_data, question)


if __name__ == "__main__":
    advisor = FarmAdvisorAPI()
    data = advisor.get_all_data()
    print("RootSense Farm Advisor")
    print(f"Location: {advisor.lat}, {advisor.lon}")
    print(f"Sensor: {data['sensor']}")
    print(f"Risk: {data['risk']['level']} ({data['risk']['score']}/10)")
