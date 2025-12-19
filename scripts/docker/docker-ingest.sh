#!/usr/bin/env sh
set -e

# Run the ingestion target inside the Docker Compose service.
ROOT_DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
cd "$ROOT_DIR"

docker compose run --rm weather-app make dwh-ingest VENV=system
