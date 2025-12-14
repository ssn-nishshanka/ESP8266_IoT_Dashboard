# IoT-Based Warehouse Environment Dashboard

This project demonstrates a complete IoT pipeline for monitoring and visualizing warehouse environmental conditions using an ESP8266, DHT11 sensor, LM393 light sensor, and a Dash web dashboard.

<img width="998" height="318" alt="image" src="https://github.com/user-attachments/assets/4d8f0503-6873-44ed-b06e-5c71a63a9342" />

## Features

* Real-time monitoring of **temperature**, **humidity**, and **light presence**.
* **Data logging** to CSV for historical analysis.
* **Interactive dashboard** built with Dash and Plotly:

  * Line charts for temperature and humidity trends
  * Gauge charts for current temperature and humidity
  * Bar chart showing light presence percentage
  * Alerts for high temperature, high humidity, or detected light
  * Summary cards showing max/min readings and light status
* Historical trend analysis with selectable days
* Live updates every 2 seconds

## Hardware

- **ESP8266** Microcontroller
- **DHT11** Temperature & Humidity Sensor
- **LM393** Light Sensor Module
- USB Cable for powering the ESP8266

## Wiring

### DHT11 Sensor
- VCC -> 3.3V (ESP8266)
- GND -> GND (ESP8266)
- DATA -> D4 (GPIO2 on ESP8266)

### LM393 Light Sensor
- VCC -> 3.3V (ESP8266)
- GND -> GND (ESP8266)
- DO (Digital Output) -> D5 (GPIO14 on ESP8266)

### Microcontroller
- ESP8266 powered via USB

<img width="705" height="397" alt="image" src="https://github.com/user-attachments/assets/70854910-2e57-49eb-8ee6-dd32e39bd94c" />

## Software

* Python 3
* Dash & Plotly
* Pandas & NumPy
* pySerial for communication with ESP8266

## File Overview

| File                                    | Description                                                       |
| --------------------------------------- | ----------------------------------------------------------------- |
| `esp8266_dht11_lm393_sensormodules.ino` | Arduino code to read sensors and send CSV data via Serial         |
| `main.py`                               | Dash dashboard that reads serial data, logs it, and visualizes it |
| `requirements.txt`                      | Python dependencies                                               |
| `sensor_log.csv`                        | Stores historical sensor readings                                 |

## Setup Instructions

### 1. Hardware

1. Connect **DHT11** to ESP8266 pin `D4`
2. Connect **LM393** to ESP8266 pin `D5`
3. Power the ESP8266 via USB

### 2. Arduino Sketch

1. Open `esp8266_dht11_lm393_sensormodules.ino` in Arduino IDE
2. Upload the sketch to ESP8266

### 3. Python Dashboard

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the dashboard:

```bash
python main.py
```

3. Open browser at `http://127.0.0.1:8050`

<img width="1815" height="851" alt="image" src="https://github.com/user-attachments/assets/58ed40c5-f804-4870-ad93-6bd4c132bf5b" />

<img width="1820" height="828" alt="image" src="https://github.com/user-attachments/assets/f43f380f-8d26-40f1-8c82-ed1303c389d1" />

<img width="1817" height="852" alt="image" src="https://github.com/user-attachments/assets/537f7b31-36f9-4a16-aef0-5e885c4585c6" />

<img width="1822" height="837" alt="image" src="https://github.com/user-attachments/assets/1c5c8e10-1e98-4da6-bf4d-bf45c05c6724" />

<img width="1823" height="806" alt="image" src="https://github.com/user-attachments/assets/9ca58619-e54b-4d98-9ccf-1cc177436c8b" />

## Usage

* Monitor **temperature**, **humidity**, and **light presence** in real-time
* Use dropdowns and sliders to view historical trends or adjust data points
* Alerts display for high temperature or humidity
