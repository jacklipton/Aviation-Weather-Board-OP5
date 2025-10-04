<div id="top"></div>

<h3 align="center">Aviation Weather Map</h3>

  <p align="center">
    A weather dependant light up aviation map.
    <br />
    <a href="https://github.com/jacklipton/Aviation-weather-board"><strong>Explore the docs »</strong></a>
    <br />
  </p>
</div>


https://github.com/jacklipton/Aviation-weather-board/assets/83594679/f8df7533-afa8-4296-8fbb-ba53487697fc

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>

<br/>


## About The Project

This project aimed to ad live weather data to a standard souther ontario VNC (VFR Navigation Chart) from NavCanada. Each airport has an LED at its location on the map and the colour of the LED corresponds to the current weather at that airport. It is designed to mimic the flight catagory feature on the maps tab in foreflight.

The board flashes either green or red when initially booted-up to indicate a successful or failed wifi connection. Each light corresponds to a specfic weather status:

* Green = VFR (Visusal Flight Rules): <i> Ceiling greater than 3000' and/or visibility greater than 5 miles</i>
* Blue = MVFR (Marginal Visual Flight Rules): <i> Ceiling between 1000' - 3000' and/or visibility between 3 - 5 miles</i>
* Red = IFR (Instrument Flight Rules): <i> Ceiling between 500' - 1000' and/or visibility between 1 - 3 miles</i>
* Pink = LIFR (Low Instrument Flight Rules): <i> Ceiling less than 500' and/or visibility less than 1</i>


### Built With

* [Micropython](https://micropython.org/) — original version (deprecated in this refactor)
* [Flask](https://flask.palletsprojects.com/) — web UI for phone control
* [CheckWX API](https://www.checkwxapi.com/)

<br/>

## Orange Pi 5 refactor (new)

This repo now includes a Linux/Python implementation suitable for Orange Pi 5 with:

- Mock GPIO for development on your laptop
- Flask web UI to control the lightboard from your phone
- Containerized dev environment targeting ARM64

### Quick start (laptop, mock mode)

1) Copy `.env.example` to `.env` and set `CHECKWX_API_KEY`.
2) Start the dev container:

```bash
docker compose -f .devcontainer/docker-compose.yml up --build
```

3) In the container, run the app:

```bash
python3 run.py
```

Open http://localhost:8080 to use the control UI.

### On Orange Pi 5 (hardware)

1) Set `.env`:
- `ENVIRONMENT=hardware`
- `CHECKWX_API_KEY=<your key>`
- Adjust `AIRPORTS`, `LED_COUNT`, `LED_ORDER` as needed.

2) Choose LED driver in `.env`:
- `LED_TYPE=APA102` (supported now)
- `LED_TYPE=WS2812` (needs driver; see notes below)

3) Run:

```bash
docker compose -f .devcontainer/docker-compose.yml up --build
python3 run.py
```

On your phone (same network), browse to `http://<pi-ip>:8080`.

### Notes on LEDs

The original MicroPython code drove a NeoPixel-like strip. Current implementation supports WS2812 via SPI bitstream on MOSI.

- WS2812/NeoPixel: Works best with a 5V data-level. If you’re not using a level shifter, keep your leads short and consider a resistor (~330Ω) in series on the data line, plus a large cap (e.g., 1000µF) across 5V–GND.
- APA102/DotStar: Not enabled, but easy to add if you switch.

If you want to change the wiring/device, set `WS2812_SPI_BUS`, `WS2812_SPI_DEVICE`, and `WS2812_SPI_SPEED_HZ` in `.env`.

## Docs

- Development: `docs/DEVELOPMENT.md`
- Orange Pi 5 deployment: `docs/DEPLOYMENT_OP5.md`
- CI/CD to Docker Hub: `docs/CI-CD.md`
- DevContainer specifics: `DEV_INSTR.md`

## Code layout

- `src/` contains all runtime code for the Orange Pi 5 version
  - `config.py` — loads `.env` and provides settings
  - `light_controller.py` — LED drivers (mock and WS2812 via SPI)
  - `weather_service.py` — fetches METARs and maps to LED colors
  - `web_server.py` — Flask app with phone UI and periodic refresh
  - `main.py` — entrypoint used by `run.py`
- Top-level MicroPython files are archived with `.backup` suffix for reference
- Use `run.py` to launch without worrying about Python module paths
* Orange Pi 5 GPIO stack: `orangepi_gpio`, `gpiozero`


## Prerequisites

Before you begin, ensure you have met the following requirements:

* Create an account with CheckWX and obtain an Auth Key
* Download the micropython firmware for your microcontroller and flash it

## Installation (Orange Pi 5)

This repo now includes a dev container that runs on your laptop or directly on the Orange Pi 5.

1) Copy `.env.example` to `.env` and set your values:
  - `CHECKWX_API_KEY` — required
  - `AIRPORTS` — comma-separated ICAO codes
  - `REFRESH_SECONDS` — default 900 (15min)
  - `LED_*` — count/pin/order

2) Start in mock mode (laptop):

```bash
ENVIRONMENT=local docker compose -f .devcontainer/docker-compose.yml up --build
```

3) Start on Orange Pi 5 with hardware:

```bash
ENVIRONMENT=hardware docker compose -f .devcontainer/docker-compose.yml up --build
```

4) Open the control UI from your phone: visit `http://<device-ip>:8080` on the same network. Use Start/Stop/Refresh.

Notes:
- The hardware LED driver needs your LED strip type (WS2812/NeoPixel vs APA102, etc.). See Issues section to confirm details.

## Contributing

Contributions are welcome! If you have any improvements, bug fixes, or feature suggestions, feel free to fork the repository and submit a pull request.


