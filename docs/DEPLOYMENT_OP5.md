# Deploying to Orange Pi 5 with Auto-Updates

This guide covers running the application on the Orange Pi 5 using Docker Compose and Watchtower for continuous deployment.

## Prerequisites

1.  **Docker & Docker Compose** installed on the OP5.
2.  **SPI Enabled**: Ensure `/dev/spidev0.0` exists.
    -   If not, use `orangepi-config` (System -> Hardware) to enable SPI.

## 1. Setup GitHub Secrets

In your GitHub Repository (Settings -> Secrets and variables -> Actions), add:
-   `DOCKERHUB_USERNAME`: Your Docker Hub username.
-   `DOCKERHUB_TOKEN`: Your Docker Hub Access Token.

This allows the GitHub Action to push new images to your account.

## 2. Prepare the Orange Pi

Create a directory for the project:
```bash
mkdir -p ~/aviation
cd ~/aviation
```

### Create the Environment File
Create a `.env` file with your production settings. You can use the `env.example` from the repo as a template.
Important settings for hardware:
```ini
ENVIRONMENT=hardware
LED_TYPE=WS2812
CHECKWX_API_KEY=your_real_api_key
# ... other settings ...
```

### Create the Docker Compose File
Copy the `docker-compose.yml` from this repository to your Orange Pi (or create it manually):

```yaml
services:
  app:
    # REPLACE with your actual image name (e.g., myuser/aviation-weather-board-op5:latest)
    image: your-dockerhub-username/aviation-weather-board-op5:latest
    container_name: avwx
    restart: unless-stopped
    ports:
      - "8080:8080"
    env_file:
      - .env
    devices:
      - "/dev/spidev0.0:/dev/spidev0.0"
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 300 --cleanup
```

## 3. Start the Application

On the Orange Pi, inside the `~/aviation` folder:

```bash
docker compose up -d
```

This will:
1.  Pull your image and start the weather board.
2.  Start **Watchtower**.

## 4. Continuous Deployment

Now, the automation is complete:

1.  **Develop**: You change code on your Mac and push to `main` on GitHub.
2.  **Build**: GitHub Actions builds the new Docker image and pushes it to Docker Hub.
3.  **Deploy**: **Watchtower** (running on your Pi) checks Docker Hub every 5 minutes. When it sees the new image, it automatically pulls it and restarts the `avwx` container.

## Troubleshooting

-   **Logs**: `docker compose logs -f app`
-   **Watchtower Logs**: `docker compose logs -f watchtower`