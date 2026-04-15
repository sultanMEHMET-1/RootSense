# RootSense Integration Guide

Use `farm_advisor_backend.py` when another frontend or service needs RootSense data without owning the weather, risk, or Gemini advisor logic.

## Required Files

- `farm_advisor_backend.py`
- `requirements.txt`

Optional:

- `farm_advisor_api.py` for a REST API wrapper
- `FLASK_API_GUIDE.md` for endpoint examples

## Basic Python Usage

```python
from farm_advisor_backend import FarmAdvisorAPI

api = FarmAdvisorAPI(latitude=40.4167, longitude=-87.3573)

data = api.get_all_data()
print(data["sensor"])
print(data["risk"])

advice = api.ask_ai_advisor("Should I irrigate today?")
print(advice)
```

## Returned Data

Sensor data:

```python
{
    "distance_cm": 31.6,
    "temperature_c": 26.1,
    "ponding_detected": False,
    "timestamp": "2026-04-15T10:30:00"
}
```

Runoff risk:

```python
{
    "score": 2,
    "level": "LOW",
    "indicator": "green",
    "factors": ["Elevated soil moisture"],
    "recommendation": "Continue normal operations and routine monitoring."
}
```

Weather forecast periods come directly from weather.gov. The app returns `None` for forecast data if the weather service is unavailable.

## REST API Usage

Start the server:

```bash
python farm_advisor_api.py
```

Fetch dashboard data from a frontend:

```javascript
async function getFarmData() {
  const response = await fetch("http://127.0.0.1:5000/api/data");
  return response.json();
}
```

Ask for AI advice:

```javascript
async function askAdvisor(question) {
  const response = await fetch("http://127.0.0.1:5000/api/advice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  return response.json();
}
```

## Configuration

Set values through environment variables or a local `.env` file:

```bash
copy .env.example .env
set GEMINI_API_KEY=your-gemini-api-key
set ROOTSENSE_LATITUDE=40.4167
set ROOTSENSE_LONGITUDE=-87.3573
```

Do not hardcode secrets in source files.
