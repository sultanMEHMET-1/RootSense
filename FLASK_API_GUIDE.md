# RootSense Flask API Guide

The Flask API wraps the shared `FarmAdvisorAPI` service for dashboards and frontend demos. It keeps the public routes stable while the shared backend handles weather lookup, runoff scoring, and Gemini advice.

## Start the Server

```bash
python farm_advisor_api.py
```

The development server runs at `http://127.0.0.1:5000`.

## Endpoints

### `GET /`

Returns API metadata and available endpoints.

### `GET /health`

Returns a simple health check:

```json
{
  "status": "ok",
  "timestamp": "2026-04-15T10:30:00"
}
```

### `GET /api/data`

Returns sensor readings, weather forecast, active alerts, and runoff risk.

```json
{
  "sensor": {
    "distance_cm": 31.6,
    "temperature_c": 26.1,
    "ponding_detected": false,
    "timestamp": "2026-04-15T10:30:00"
  },
  "weather": [],
  "alerts": [],
  "risk": {
    "score": 2,
    "level": "LOW",
    "indicator": "green",
    "factors": [],
    "recommendation": "Continue normal operations and routine monitoring."
  },
  "timestamp": "2026-04-15T10:30:00"
}
```

### `GET /api/sensor`

Returns the current simulated RootSense sensor reading.

### `GET /api/weather`

Returns up to seven weather.gov forecast periods. Returns `503` when forecast data is unavailable.

### `GET /api/alerts`

Returns active weather alerts for the configured location.

### `GET /api/risk`

Returns a runoff-risk assessment.

### `POST /api/advice`

Calls Gemini and returns farm-management advice. `GEMINI_API_KEY` must be configured in the environment or local `.env` file for model output. If the key is missing, this endpoint returns a setup message while the non-AI endpoints continue to work.

Request:

```json
{
  "question": "Should I irrigate today?"
}
```

Response:

```json
{
  "question": "Should I irrigate today?",
  "advice": "Gemini-backed advice text...",
  "timestamp": "2026-04-15T10:35:00"
}
```

### `POST /api/location`

Updates the weather location for the running server.

Request:

```json
{
  "latitude": 40.4167,
  "longitude": -87.3573
}
```

## Frontend Example

```javascript
async function fetchDashboardData() {
  const response = await fetch("http://127.0.0.1:5000/api/data");
  return response.json();
}

async function askAdvisor(question) {
  const response = await fetch("http://127.0.0.1:5000/api/advice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  return response.json();
}
```

## Smoke Test

Start the server, then run:

```bash
python test_api.py
```
