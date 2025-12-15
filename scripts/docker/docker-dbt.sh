#!/usr/bin/env sh
set -e

# Run dbt build inside the Docker Compose service.
ROOT_DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
cd "$ROOT_DIR"

docker compose run --rm weather-app make dbt-build VENV=system
