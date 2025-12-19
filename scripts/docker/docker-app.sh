#!/usr/bin/env sh
set -e

# Run the Streamlit app inside the Docker Compose service with ports exposed.
ROOT_DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
cd "$ROOT_DIR"

docker compose run --rm --service-ports weather-app streamlit run apps/bi-streamlit/app.py
