# RootSense Farm Advisor

The Farm Advisor is the Python side of RootSense. It combines simulated field sensor data, NOAA weather data, runoff-risk scoring, and Gemini-powered recommendations.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure Gemini

Do not commit API keys. Copy the example file and put your real key in the local `.env`, or export the same value in your shell:

```bash
copy .env.example .env
set GEMINI_API_KEY=your-gemini-api-key
```

The app loads `.env` automatically. Without this key, sensor, weather, and risk data still work, but Gemini advice requests return a setup message instead of model output.

## Run Options

Command-line demo:

```bash
python farm_advisor.py
```

Tkinter dashboard:

```bash
python farm_advisor_gui.py
```

Flask API:

```bash
python farm_advisor_api.py
```

## Environment Variables

- `GEMINI_API_KEY`: enables Gemini-backed farm-advisor responses.
- `GEMINI_MODEL`: overrides the Gemini model name. Defaults to `gemini-2.0-flash`.
- `ROOTSENSE_LATITUDE`: default API latitude. Defaults to `40.4167`.
- `ROOTSENSE_LONGITUDE`: default API longitude. Defaults to `-87.3573`.

## Hardware Integration Path

`SensorData.get_current_readings()` currently generates demo readings for the Python app. Replace that method with serial, file, or network telemetry from the STM32 firmware when the hardware data pipeline is ready.
