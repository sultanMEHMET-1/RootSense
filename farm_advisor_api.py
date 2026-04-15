#!/usr/bin/env python3
"""Flask REST API for the RootSense farm-advisor demo."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS

from farm_advisor_backend import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, FarmAdvisorAPI


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def create_advisor() -> FarmAdvisorAPI:
    return FarmAdvisorAPI(
        latitude=_float_env("ROOTSENSE_LATITUDE", DEFAULT_LATITUDE),
        longitude=_float_env("ROOTSENSE_LONGITUDE", DEFAULT_LONGITUDE),
    )


app = Flask(__name__)
CORS(app)
advisor = create_advisor()


@app.get("/")
def index():
    return jsonify(
        {
            "name": "RootSense Farm Advisor API",
            "endpoints": {
                "GET /health": "API health check",
                "GET /api/data": "Sensor, weather, alerts, and runoff risk",
                "GET /api/sensor": "Current simulated sensor readings",
                "GET /api/weather": "Weather forecast",
                "GET /api/alerts": "Active weather alerts",
                "GET /api/risk": "Runoff risk assessment",
                "POST /api/advice": "AI farming advice",
                "POST /api/location": "Update latitude and longitude",
            },
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.get("/api/data")
def get_data():
    return jsonify(advisor.get_all_data())


@app.get("/api/sensor")
def get_sensor():
    return jsonify(advisor.get_sensor_data())


@app.get("/api/weather")
def get_weather():
    forecast = advisor.get_weather_forecast()
    if forecast is None:
        return jsonify({"error": "Weather forecast unavailable"}), 503
    return jsonify(forecast)


@app.get("/api/alerts")
def get_alerts():
    return jsonify(advisor.get_weather_alerts())


@app.get("/api/risk")
def get_risk():
    return jsonify(advisor.calculate_runoff_risk())


@app.post("/api/advice")
def get_advice():
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()

    if not question:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    return jsonify(
        {
            "question": question,
            "advice": advisor.ask_ai_advisor(question),
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.post("/api/advisor/ask")
def ask_advisor_legacy():
    response = get_advice()
    return response


@app.post("/api/location")
def update_location():
    global advisor

    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    try:
        latitude = float(payload["latitude"])
        longitude = float(payload["longitude"])
    except (KeyError, TypeError, ValueError):
        return (
            jsonify(
                {
                    "error": "Request body must include numeric latitude and longitude"
                }
            ),
            400,
        )

    advisor = FarmAdvisorAPI(latitude=latitude, longitude=longitude)
    return jsonify(
        {
            "message": "Location updated successfully",
            "latitude": latitude,
            "longitude": longitude,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
