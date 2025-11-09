# Makefile — dbt-weather-poc
# Usage: make <cible> (ex : make ingest DEPT=09)

# ========== Configuration ==========
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip
DBT_PROJECT := dbt_weather

# Scripts et modules ingestion
SCRIPT_FETCH  := scripts/ingestion/fetch_meteofrance_paquetobs.py
MODULE_WRITE  := scripts.ingestion.write_duckdb_raw

# DB / Tools
DBPATH := data/warehouse.duckdb
DUCKDB := duckdb
DBT    := dbt

# Paramètres (overridable)
DEPT    ?= 9
TABLE   ?= raw.obs_hourly

.PHONY: help tree \
		env-setup env-lock env-clean env-activate \
		api-check \
		dwh-ingest dwh-reset dwh-tables \
		dwh-table-info dwh-table-shape dwh-table-sample dwh-table \
		dbt-build dbt-test dbt-rebuild \
		dbt-sources-test dbt-sources-freshness dbt-sources-check \
		py-lint py-fmt sql-lint sql-fmt

# ========== Default / Help ==========
.DEFAULT_GOAL := help
help: ## Affiche cette aide
	@printf "Cibles disponibles :\n\n"
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) \
	 | sed -E 's/:.*##/\t- /'

tree: ## Affiche la structure du repo
	tree -I 'node_modules|.git|dist|build|venv|__pycache__|dbt_utils|target'
	
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

dwh-ingest: ## Ingestion raw DuckDB (dept configuré via DEPT=)
	$(PY) -m $(MODULE_WRITE) --dept $(DEPT)

# ========== DuckDB ==========
dwh-tables: ## Liste les tables + schémas
	$(DUCKDB) $(DBPATH) -c "SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name;"

dwh-table-info: ## Affiche les colonnes d’une table (PRAGMA table_info)
	$(DUCKDB) $(DBPATH) -c "PRAGMA table_info('$(TABLE)');"

dwh-table-shape: ## Affiche les dimensions (nrows, ncols) d'une table
	$(DUCKDB) $(DBPATH) -c "WITH s AS ( \
	  SELECT \
	    (SELECT COUNT(*) FROM $(TABLE)) AS nrows, \
	    (SELECT COUNT(*) FROM pragma_table_info('$(TABLE)')) AS ncols \
	) \
	SELECT nrows, ncols FROM s;"
	
dwh-table-sample: ## Extrait d'une table
	$(PY) scripts/utils/peek_duckdb.py --table $(TABLE)

dwh-table: dwh-table-shape dwh-table-info dwh-table-sample

dwh-reset: ## Réinitialise les schémas calculés (staging/intermediate/marts)
	@echo "🧹 Cleaning warehouse (keeping raw)..."
	@echo "DROP SCHEMA IF EXISTS staging CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS intermediate CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS marts CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "✅ Warehouse reset complete."

# ========== DBT ==========
dbt-build: ## dbt deps + dbt run
	$(DBT) deps
	$(DBT) run

dbt-test: ## dbt test
	$(DBT) test

dbt-rebuild: ## Full refresh (reset + deps + run --full-refresh + test)
	@$(MAKE) dbt-reset
	$(DBT) deps
	$(DBT) run --full-refresh
	$(DBT) test
	@echo "✅ DBT full refresh complete."

# ========== Sources DBT ==========
dbt-sources-test: ## DBT : tests sur les sources (schema raw)
	$(DBT) test --select "source:*"

dbt-sources-freshness: ## Vérifie la fraîcheur loaded_at_field des sources
	$(DBT) source freshness

dbt-sources-check: dbt-sources-test dbt-sources-freshness ## Test + freshness combo

# ========== Lint ==========
py-lint: ## Lint Python via ruff
	$(VENV)/bin/ruff check .

py-fmt: ## Format Python via ruff format
	$(VENV)/bin/ruff format .

sql-lint: ## Lint SQL via sqlfluff
	$(VENV)/bin/sqlfluff lint $(DBT_PROJECT)

sql-fmt: ## Format SQL via sqlfluff fix
	$(VENV)/bin/sqlfluff fix $(DBT_PROJECT) --rules LT08,LT09,LT10,LT12,AL01
