# CI/CD: Build and Publish Docker Images via GitHub Actions

This repo ships with a GitHub Actions workflow that automatically builds a multi-architecture Docker image and pushes it to Docker Hub whenever you push to `main` or create a version tag.

## What you get

- Multi-arch image for linux/amd64 and linux/arm64 (works on laptops and Orange Pi 5)
- Auto-tagging scheme:
  - `latest` on pushes to `main`
  - `<branch>` for non-main branches (e.g., `feature-x`)
  - `sha-<short>` for each commit
  - Semantic version tags when you push a tag like `v1.2.3` (`1.2` also)

Image name: `docker.io/<your-dockerhub-username>/<repo-name>`

## One-time setup

1) Create a Docker Hub account if you don’t have one.
2) In your GitHub repository Settings → Secrets and variables → Actions, add these Repository secrets:
   - `DOCKERHUB_USERNAME` — your Docker Hub username
   - `DOCKERHUB_TOKEN` — a Docker Hub access token (Docker Hub → Account Settings → Security → New Access Token)

No other secrets are required. The workflow derives the image name from the repo name and your Docker Hub username.

## How it works

Workflow file: `.github/workflows/docker-build-push.yml`

- Triggers on pushes to `main` and on tags matching `v*.*.*`.
- Uses `docker/setup-qemu-action` to enable cross-building.
- Uses `docker/setup-buildx-action` to set up the Buildx builder.
- Logs in to Docker Hub using the secrets.
- Uses `docker/metadata-action` to generate image tags and labels.
- Builds with `docker/build-push-action` and pushes images for `linux/amd64` and `linux/arm64`.

## Daily use

- Push to `main` → publishes `latest`, `main`, and `sha-<short>` tags.
- Open a PR from a branch → CI will build and push a `<branch>` tag to Docker Hub (useful for testing).
- Create a release tag, e.g. `git tag v1.2.3 && git push --tags` → publishes `1.2`, `1.2.3`, and `sha-<short>` tags.

## Pulling on Orange Pi 5

Example pull and run commands (replace `<user>` and `<repo>`):

```bash
# Pull the latest arm64 image
sudo docker pull docker.io/<user>/<repo>:latest

# Run (ensure your .env is present and located at /opt/aviation/.env)
sudo docker run -d --name aviation-weather \
  --env-file /opt/aviation/.env \
  --device /dev/spidev0.0 \
  -p 8080:8080 \
  docker.io/<user>/<repo>:latest
```

Tip: set `ENVIRONMENT=hardware` in your `.env` on the OP5.

## Troubleshooting

- “denied: requested access to the resource is denied” → Verify `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets and that the repository exists (Docker Hub will auto-create on first push).
- Buildx not found or QEMU errors → The workflow sets those up; if errors persist, re-run the job.
- Wrong image name → The name is computed as `${{ secrets.DOCKERHUB_USERNAME }}/${{ github.event.repository.name }}`. If you need a custom name, edit `images:` in the workflow.

## Advanced: Matrix and caching

- To add more platforms, update `platforms:` in the build step.
- GitHub cache could be enabled by adding `cache-from`/`cache-to` to `docker/build-push-action` for faster rebuilds.
