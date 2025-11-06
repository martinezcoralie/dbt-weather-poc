# Makefile — dbt-weather-poc
# Usage: make <cible> (ex : make ingest DEPT=09)

# ========== Configuration ==========
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip

# Scripts et modules ingestion
SCRIPT_FETCH  := scripts/ingestion/fetch_meteofrance_paquetobs.py
MODULE_WRITE  := scripts.ingestion.write_duckdb_raw

# DB / Tools
DBPATH := warehouse.duckdb
DUCKDB := duckdb
DBT    := dbt

# Paramètres (overridable)
DEPT    ?= 9
TABLE   ?= raw.obs_hourly

.PHONY: help \
        env-setup env-lock env-clean env-activate \
        api-check ingest \
        db-peek db-tables db-reset db-build db-test db-rebuild \
        db-sources-test db-sources-freshness db-sources-check \
        db-table-info

# ========== Default / Help ==========
.DEFAULT_GOAL := help
help: ## Affiche cette aide
	@printf "Cibles disponibles :\n\n"
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) \
	 | sed -E 's/:.*##/\t- /'

# ========== Environnement Python ==========
env-setup: ## Crée le virtualenv et installe les dépendances
	@test -d $(VENV) || python -m venv $(VENV)
	$(PIP) install -r requirements.txt

env-lock: env-setup ## Gèle les versions dans requirements.lock
	$(PIP) freeze > requirements.lock

env-clean: ## Supprime complètement le venv
	rm -rf $(VENV)

env-activate: ## Affiche la commande d'activation du venv
	@echo "To activate:"
	@echo "  source $(VENV)/bin/activate"

# ========== API & Ingestion ==========
api-check: ## Test rapide API + scripts ingestion
	$(PY) $(SCRIPT_FETCH) --list-stations --head 5
	$(PY) $(SCRIPT_FETCH) --dept $(DEPT) --head 5

ingest: ## Ingestion raw DuckDB (dept configuré via DEPT=)
	$(PY) -m $(MODULE_WRITE) --dept $(DEPT)

# ========== DuckDB ==========
db-peek: ## Aperçu complet du contenu DuckDB
	$(PY) scripts/utils/peek_duckdb.py

db-tables: ## Liste les tables + schémas
	$(DUCKDB) $(DBPATH) -c "SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name;"

db-table-info: ## Affiche les colonnes d’une table (PRAGMA table_info)
	$(DUCKDB) $(DBPATH) -c "PRAGMA table_info('$(TABLE)');"

db-reset: ## Réinitialise les schémas calculés (staging/intermediate/marts)
	@echo "🧹 Cleaning warehouse (keeping raw)..."
	@echo "DROP SCHEMA IF EXISTS staging CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS intermediate CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS marts CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "✅ Warehouse reset complete."

# ========== DBT ==========
db-build: ## dbt deps + dbt run
	$(DBT) deps
	$(DBT) run

db-test: ## dbt test
	$(DBT) test

db-rebuild: ## Full refresh (reset + deps + run --full-refresh + test)
	@$(MAKE) db-reset
	$(DBT) deps
	$(DBT) run --full-refresh
	$(DBT) test
	@echo "✅ DBT full refresh complete."

# ========== Sources DBT ==========
db-sources-test: ## DBT : tests sur les sources (schema raw)
	$(DBT) test --select "source:*"

db-sources-freshness: ## Vérifie la fraîcheur loaded_at_field des sources
	$(DBT) source freshness

db-sources-check: db-sources-test db-sources-freshness ## Test + freshness combo

# ========== Lint ==========
py-lint: ## Lint Python via ruff
	$(VENV)/bin/ruff check .

py-fmt: ## Format Python via ruff format
	$(VENV)/bin/ruff format .

sql-lint: ## Lint SQL via sqlfluff
	$(VENV)/bin/sqlfluff lint .

sql-fmt: ## Format SQL via sqlfluff fix
	$(VENV)/bin/sqlfluff fix .

yaml-lint: ## Lint YAML via yamllint
	$(VENV)/bin/yamllint .
