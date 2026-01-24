<div id="top"></div>

<h3 align="center">Aviation Weather Map (Orange Pi 5 Edition)</h3>

  <p align="center">
    A weather-dependent light-up aviation map powered by an Orange Pi 5.
    <br />
    <a href="https://github.com/jacklipton/Aviation-weather-board"><strong>Explore the docs »</strong></a>
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation-production">Installation (Production)</a></li>
        <li><a href="#installation-development">Installation (Development)</a></li>
      </ul>
    </li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>

<br/>

## About The Project

This project visualizes live weather data on a VNC (VFR Navigation Chart) map. Each airport is represented by an LED that changes color based on the current METAR flight category, mimicking the features found in ForeFlight.

**Status Colors:**
* **Green** = VFR (Visual Flight Rules)
* **Blue** = MVFR (Marginal Visual Flight Rules)
* **Red** = IFR (Instrument Flight Rules)
* **Pink** = LIFR (Low Instrument Flight Rules)

**New in this version:**
* **Orange Pi 5 Support**: Optimized for the OP5 hardware using SPI for reliable LED timing.
* **Dockerized**: Runs in a container for easy deployment and isolation.
* **Auto-Updating**: Uses Watchtower to automatically pull and restart the app when you push code to GitHub.
* **Web UI**: Control the board (Start/Stop/Refresh) from your phone.

## Architecture

* **Hardware**: Orange Pi 5 (running Linux)
* **Language**: Python 3.11
* **LED Driver**: WS2812 (NeoPixel) driven via SPI (MOSI) for high-precision timing.
* **Web Server**: Flask
* **Deployment**: Docker Compose + Watchtower

## Getting Started

### Prerequisites

* **Orange Pi 5** with Docker and Docker Compose installed.
* **WS2812 LED Strip** wired to the SPI0 MOSI pin (with 5V power).
* **CheckWX API Key**: Get one for free at [CheckWX](https://www.checkwxapi.com/).

### Installation (Production)

This setup runs on the Orange Pi 5 and stays up-to-date automatically.

1.  **Prepare the Pi**:
    Create a directory and download the production files:
    ```bash
    mkdir -p ~/aviation
    cd ~/aviation
    wget https://raw.githubusercontent.com/jacklipton/Aviation-weather-board/main/docker-compose.yml
    wget https://raw.githubusercontent.com/jacklipton/Aviation-weather-board/main/.env.example -O .env
    ```

2.  **Configure**:
    Edit the `.env` file with your API key and settings:
    ```bash
    nano .env
    # Set CHECKWX_API_KEY, AIRPORTS, etc.
    # Ensure ENVIRONMENT=hardware
    ```

3.  **Run**:
    ```bash
    docker compose up -d
    ```

The board will light up. Visit `http://<pi-ip>:8080` to control it.
*See `docs/DEPLOYMENT_OP5.md` for full deployment details.*

### Installation (Development)

Run the code on your Mac/PC with "Mock" LEDs to test logic.

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/jacklipton/Aviation-weather-board.git
    cd Aviation-weather-board
    ```

2.  **Setup Environment**:
    ```bash
    cp .env.example .env
    # Set CHECKWX_API_KEY
    # Ensure ENVIRONMENT=local
    ```

3.  **Run Tests**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 -m unittest discover tests
    ```

4.  **Run App**:
    ```bash
    python3 run.py
    ```
    Open `http://localhost:8080`.

## Configuration

All settings are managed via the `.env` file or environment variables.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `CHECKWX_API_KEY` | **Required** API Key from CheckWX | `None` |
| `ENVIRONMENT` | `hardware` (OP5) or `local` (Mac/PC) | `local` |
| `REFRESH_SECONDS` | How often to fetch new weather | `900` (15 min) |
| `AIRPORTS` | Comma-separated list of ICAO codes | `CYGK,CYHM...` |
| `LED_ORDER` | Mapping of airport index to LED pixel index | `14,41...` |
| `WS2812_SPI_BUS` | SPI Bus ID for LEDs (on OP5) | `0` |

## Contributing

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License.