# 🧠 Orange Pi 5 Dev Environment

A cross-platform development setup for building and testing GPIO, I²C, SPI, and UART functionality on **Orange Pi 5** — while being able to develop and debug on your **laptop** first.

---

## ⚙️ Overview

This project provides:

- **Docker + VS Code Dev Container** setup for Ubuntu 22.04 (ARM64)
- **Mock GPIO mode** for development on your laptop
- **Real hardware mode** when running directly on the Orange Pi 5
- Unified environment — same container runs everywhere

---

## 🧩 Project structure

```
orange-pi-dev/
├── .devcontainer/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── devcontainer.json
├── src/
│   ├── main.py
│   └── gpio_manager.py
├── requirements.txt
└── .env
```

---

## 🐍 Python environment

| Library | Purpose |
|----------|----------|
| `gpiozero` | General GPIO API + mock support |
| `orangepi_gpio` | Real hardware GPIO on Orange Pi 5 |
| `smbus2` | I²C support |
| `spidev` | SPI support |

---

## 🔄 Development workflow

### 1. On your **laptop**
Develop and test logic using mock GPIOs.

```bash
# Default: mock mode
ENVIRONMENT=local
docker compose up --build
```

- Uses `gpiozero.MockFactory`  
- No hardware required  
- Perfect for rapid iteration  

### 2. On the **Orange Pi 5**
Run and debug with real GPIO/I²C/SPI devices.

```bash
export ENVIRONMENT=hardware
docker compose up --build
```

- Runs in privileged mode  
- Mounts `/dev/gpiomem`, `/dev/i2c-*`, `/dev/spidev*`  
- Full hardware access  

---

## 🧰 Mock vs Hardware

| Mode | Variable | Behaviour |
|------|-----------|------------|
| Laptop (mock) | `ENVIRONMENT=local` | Safe simulation using gpiozero |
| Orange Pi 5 (hardware) | `ENVIRONMENT=hardware` | Uses `orangepi_gpio` + hardware devices |

Switch modes by editing `.env` or setting `export ENVIRONMENT=...`.

---

## 🧠 Tips

- Use `docker buildx` on x86 laptops to build ARM64 images:  
  ```bash
  docker buildx create --use
  docker buildx build --platform linux/arm64 -t orange-pi-dev .
  ```
- Push your image to Docker Hub or save as `.tar` for transfer.
- You can extend this environment with C/C++ or Node bindings for GPIO.

---

## 🧩 VS Code Dev Container

Open this folder in VS Code →  
**F1 → “Dev Containers: Reopen in Container”**

You’ll get:
- Fully reproducible Ubuntu 22.04 (ARM64) environment
- Python + GPIO libraries
- Docker integration and terminal access

---

## 🚀 Example run

```bash
cd src
python3 main.py
```

Expected output:
```
🧪 Using mock GPIO (laptop)
Blinking LED on pin 17
```

On the Orange Pi 5:
```
🔧 Using real GPIO (Orange Pi)
Blinking LED on pin 17
```

---

## 📤 Transferring the image

You can share the same image between your laptop and the Pi:

### Option 1: Docker Hub
```bash
# Tag and push
docker tag orange-pi-dev yourname/orange-pi-dev:latest
docker push yourname/orange-pi-dev:latest
```

On the Pi:
```bash
docker pull yourname/orange-pi-dev:latest
docker compose up
```

### Option 2: Save and load manually
```bash
# On laptop
docker save -o orange-pi-dev.tar orange-pi-dev

# Copy to Pi (e.g. via scp)
scp orange-pi-dev.tar orangepi@<pi_ip>:/home/orangepi/

# On Pi
docker load -i orange-pi-dev.tar
docker compose up
```

---

## 📜 Licence

MIT — feel free to modify and reuse for your own Orange Pi projects.
