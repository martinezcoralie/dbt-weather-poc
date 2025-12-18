#!/bin/sh
set -eu

DUCKDB_PATH="${DUCKDB_PATH:-/app/data/warehouse.duckdb}"
DEMO_DUCKDB_PATH="${DEMO_DUCKDB_PATH:-/app/demo/demo_warehouse.duckdb}"

mkdir -p "$(dirname "$DUCKDB_PATH")"

if [ ! -f "$DUCKDB_PATH" ]; then
  echo "[init] DuckDB introuvable dans le volume -> seed depuis la démo"
  if [ ! -f "$DEMO_DUCKDB_PATH" ]; then
    echo "[init] ERREUR: fichier démo introuvable: $DEMO_DUCKDB_PATH" >&2
    exit 1
  fi
  cp "$DEMO_DUCKDB_PATH" "$DUCKDB_PATH"
else
  echo "[init] DuckDB déjà présent -> pas de seed"
fi

exec "$@"
