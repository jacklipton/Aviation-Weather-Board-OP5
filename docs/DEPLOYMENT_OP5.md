# Deploying to Orange Pi 5

This guide covers running the Docker image on the Orange Pi 5.

## Prerequisites

- Docker installed on the OP5
- SPI device enabled (e.g., `/dev/spidev0.0`) and wired to your WS2812 data pin
- 5V power for LEDs, common ground, resistor/capacitor recommended for WS2812

## Configure environment

On your workstation, prepare an `.env` with:

```
ENVIRONMENT=hardware
LED_TYPE=WS2812
CHECKWX_API_KEY=your_key
AUTH_USERNAME=your_user
AUTH_PASSWORD=your_pass
AIRPORTS=CYGK,CYHM,CYKF,CYND,CYOO,CYOW,CYPQ,CYQA,CYSN,CYTR,CYTZ,CYXU,CYYZ,KBUF,KIAG,KMSS,KOGS
LED_COUNT=50
LED_ORDER=14,41,44,8,21,7,19,26,35,17,31,48,32,38,36,4,1
WS2812_SPI_BUS=0
WS2812_SPI_DEVICE=0
WS2812_SPI_SPEED_HZ=3200000
HOST=0.0.0.0
PORT=8080
```

Copy it to the OP5 (e.g., `/home/orangepi/aviation/.env`).

## Pull and run

```
docker pull youruser/aviation-weather:latest

docker run -d \
  --name avwx \
  --restart unless-stopped \
  --env-file /home/orangepi/aviation/.env \
  --device /dev/spidev0.0:/dev/spidev0.0 \
  -p 8080:8080 \
  youruser/aviation-weather:latest
```

Open `http://<pi-ip>:8080` on your phone (use Basic Auth if set).

## Updating

```
docker pull youruser/aviation-weather:latest

docker stop avwx && docker rm avwx

docker run -d ... (same as above)
```
