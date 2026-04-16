# RootSense

RootSense is a field-edge monitoring prototype for runoff-risk awareness. It combines STM32 firmware for local sensor signaling with a Python farm-advisor layer that pulls NOAA weather data, scores runoff risk, and calls the Gemini API for field-management recommendations.

## What It Does

- Reads or simulates field conditions such as water distance, ponding, and temperature.
- Classifies runoff risk as low, moderate, or high from sensor and forecast data.
- Exposes the advisor logic through a reusable Python module, CLI, Tkinter GUI, and Flask API.
- Calls Gemini for natural-language farm advice while keeping `GEMINI_API_KEY` out of source code.
- Includes STM32F091 firmware and a Makefile for the embedded proof of concept.

## Repository Layout

```text
.
|-- src/                       STM32 application sources
|-- Drivers/                   STM32 CMSIS/HAL vendor files
|-- Makefile                   Firmware build targets
|-- farm_advisor_backend.py    Shared weather, sensor, risk, and AI logic
|-- farm_advisor_api.py        Flask REST API
|-- farm_advisor.py            Command-line demo
|-- farm_advisor_gui.py        Tkinter dashboard demo
|-- tests/                     Python unit tests
|-- FLASK_API_GUIDE.md         REST API usage guide
|-- README_ADVISOR.md          Advisor setup notes
|-- README_INTEGRATION.md      Frontend/backend integration notes
```

## Python Quick Start

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Gemini setup:

```bash
copy .env.example .env
set GEMINI_API_KEY=your-gemini-api-key
```

The app loads `.env` automatically during local development.

Run the CLI demo:

```bash
python farm_advisor.py
```

Run the Flask API:

```bash
python farm_advisor_api.py
```

Then open `http://127.0.0.1:5000` or call `GET /api/data`.

## Firmware Build

The firmware targets an STM32F091RCT6-class Cortex-M0 board and expects the ARM embedded GCC toolchain on your path. The active entrypoint in `src/main.c` reads an ultrasonic distance sensor, samples an AD8495 temperature input on ADC, estimates ponding depth against a calibrated dry baseline, and drives green/yellow/red LEDs for low, moderate, and high runoff risk.

```bash
make
```

The default build artifacts are written under `build/` as `rootsense-firmware.elf`, `.bin`, `.hex`, and `.map`.

Useful targets:

```bash
make clean
make flash
```

## API Highlights

- `GET /api/data` returns sensor readings, forecast, alerts, and runoff risk.
- `GET /api/risk` returns the current runoff-risk score and recommendation.
- `POST /api/advice` accepts `{"question": "Should I irrigate today?"}` and returns Gemini-backed farm advice.
- `POST /api/location` updates the weather location for the running server.

See [FLASK_API_GUIDE.md](FLASK_API_GUIDE.md) for request and response examples.

## Testing

Run the unit tests:

```bash
python -m unittest discover
```

To smoke-test the local Flask API after starting the server:

```bash
python test_api.py
```

## Notes

- Sensor readings in the Python demo are simulated until real serial or telemetry integration is connected.
- weather.gov only supports United States locations.
- Gemini-backed advice requires `GEMINI_API_KEY`; missing keys are reported by advice endpoints only, while sensor, weather, and runoff-risk data continue to work.

## License

MIT License. See [LICENSE](LICENSE).
