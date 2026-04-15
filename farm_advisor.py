#!/usr/bin/env python3
"""Command-line RootSense farm-advisor demo."""

from __future__ import annotations

from datetime import datetime

from farm_advisor_backend import FarmAdvisorAPI, SensorData


def print_section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def print_sensor_data(sensor_data):
    print_section("RootSense Field Sensors")
    print(f"Reading time: {sensor_data['timestamp']}")
    print(f"Distance to surface: {sensor_data['distance_cm']:.1f} cm")
    print(f"Temperature: {sensor_data['temperature_c']:.1f} C")
    print(f"Ponding detected: {'yes' if sensor_data['ponding_detected'] else 'no'}")
    print("Field conditions:")
    for condition in SensorData.assess_conditions(sensor_data):
        print(f"  - {condition}")


def print_risk(risk):
    print_section("Runoff Risk")
    print(f"Level: {risk['level']} ({risk['score']}/10)")
    print(f"Indicator: {risk['indicator']}")
    print(f"Recommendation: {risk['recommendation']}")
    if risk["factors"]:
        print("Factors:")
        for factor in risk["factors"]:
            print(f"  - {factor}")


def print_weather(forecast, alerts):
    print_section("Weather")
    if alerts:
        print("Active alerts:")
        for alert in alerts[:3]:
            props = alert.get("properties", {})
            print(f"  - {props.get('event', 'Alert')}: {props.get('headline', '')}")
    else:
        print("No active weather alerts returned.")

    if forecast:
        print()
        print("Forecast:")
        for period in forecast[:4]:
            precip = (
                period.get("probabilityOfPrecipitation", {}).get("value", 0) or 0
            )
            print(
                f"  - {period['name']}: {period['shortForecast']}, "
                f"{period['temperature']} {period['temperatureUnit']}, "
                f"{precip}% precipitation"
            )
    else:
        print("Weather forecast unavailable.")


def main() -> None:
    api = FarmAdvisorAPI()
    data = api.get_all_data()

    print("=" * 70)
    print("RootSense Farm Advisor")
    print("Weather-aware field monitoring and runoff-risk advice")
    print("=" * 70)
    print(f"Location: {api.lat}, {api.lon}")

    print_sensor_data(data["sensor"])
    print_risk(data["risk"])
    print_weather(data["weather"], data["alerts"])

    print_section("AI Advisor")
    print("Set GEMINI_API_KEY to enable Gemini-powered advice.")
    question = input("Ask a field-management question, or press Enter to skip: ").strip()
    if question:
        print()
        print(api.ask_ai_advisor(question))

    print()
    print("Report generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
