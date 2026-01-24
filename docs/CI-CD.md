# CI/CD: Build and Publish Docker Images via GitHub Actions (Self-Hosted)

This repo includes a GitHub Actions workflow that builds the Docker image **directly on your Orange Pi 5** and pushes it to Docker Hub.

## How it works

1.  **Runner**: The workflow is configured to run on `[self-hosted, linux, arm64]`. This matches your Orange Pi 5 setup.
2.  **Native Build**: Since the runner is ARM64 and the target is ARM64, builds are native and extremely fast. No QEMU emulation is required.
3.  **Deployment**: Watchtower (running on the Pi) sees the new image on Docker Hub and updates the running container.

## Setup Requirements

### 1. GitHub Secrets
In Repository Settings → Secrets and variables → Actions, add:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

### 2. Self-Hosted Runner
You must install the GitHub Actions Runner on your Orange Pi 5.
1.  Go to Repo Settings → Actions → Runners → New self-hosted runner.
2.  Select **Linux** and **ARM64**.
3.  Follow the instructions to download and configure the agent on your Pi.
4.  Run `./svc.sh install` and `./svc.sh start` to keep it running in the background.

## Workflow File

File: `.github/workflows/docker-build-push.yml`

- Triggers on:
  - Push to `main`
  - Push to tags (e.g., `v1.0.0`)
  - Manual trigger (`workflow_dispatch`)
- Actions:
  - Checks out code.
  - Logs in to Docker Hub.
  - Builds `Dockerfile.prod` for `linux/arm64`.
  - Pushes to Docker Hub with tags (`latest`, `main`, `sha`, etc.).

## Troubleshooting

- **"Runner not found"**: Ensure your Orange Pi is powered on and the runner service is active (`sudo ./svc.sh status`).
- **"Permission denied"**: Ensure the `orangepi` user (or whichever user runs the agent) is in the `docker` group: `sudo usermod -aG docker $USER`.