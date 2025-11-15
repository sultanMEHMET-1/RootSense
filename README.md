# RootSense

**A Field-Edge Micro-Station for Real-Time Runoff Risk**

---

## Overview
RootSense is a low-cost, Arduino-based micro-station designed to provide farmers and land managers with **real-time runoff risk alerts** at the edge of their fields. By combining soil, weather, and environmental signals, RootSense helps farmers make informed decisions to **protect yields, reduce nutrient loss, and save costs**.

---

## Key Features
- **Soil Moisture Monitoring** – Detect saturated conditions that increase runoff risk.  
- **Weather Awareness** – Temperature, humidity, and light sensors help predict storm onset.  
- **Instant Alerts** – LED indicators, LCD display, and buzzer for LOW / MEDIUM / HIGH runoff risk.  
- **Hyper-Local Data** – Field-level sensing complements broader watershed monitoring.  
- **Low-Cost & Open-Source** – Built with an Arduino Uno and commonly available sensors.  

---

## Hardware Components
- Arduino Uno (Elegoo or compatible)  
- Capacitive Soil Moisture Sensor  
- DHT22 / BME280 (Temp + Humidity + Pressure)  
- Light Sensor (LDR / BH1750)  
- Rain Sensor (optional)  
- LED indicators  
- Buzzer  
- LCD Display  

---

## How It Works
1. Sensors continuously measure soil moisture, temperature, humidity, light, and rainfall.  
2. Arduino calculates a **Runoff Risk Index** based on combined sensor readings.  
3. LCD displays the current risk: `LOW`, `MEDIUM`, or `HIGH`.  
4. LED colors and buzzer provide instant, intuitive alerts for immediate action.  

---

## Demo / Simulation
- Pour water on the soil probe → LED turns red, buzzer sounds, LCD shows `HIGH RUNOFF RISK`.  
- Use light shading to simulate cloud cover → risk adjusts accordingly.  
- Ideal for hackathon demos and educational use.  

---

## Future Extensions
- Add **ultrasonic water-level sensor** for ditch monitoring.  
- Connect multiple RootSense nodes for **field network monitoring**.  
- Integrate **mobile notifications or cloud logging** for remote farmers.  
- Calibrate Runoff Risk Index with real local watershed data for improved accuracy.  

---

## License
MIT License – Open-source hardware and code.
