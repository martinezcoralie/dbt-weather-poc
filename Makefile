# Makefile — dbt-weather-poc
# Usage: make <cible> (ex : make ingest DEPT=09)

# ========== Configuration ==========
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip
DBT_PROJECT := weather_dbt

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
		dbt-docs-generate dbt-docs-serve dbt-docs \
		py-lint py-fmt sql-lint sql-fmt

# ========== Default / Help ==========
.DEFAULT_GOAL := help
help: ## Affiche cette aide avec la liste des commandes Make
	@printf "Cibles disponibles :\n\n"
	@awk 'BEGIN {FS = ":.*##"; printf "%-25s %s\n", "Commande", "Description"; print "-----------------------------------------------"} \
	     /^[a-zA-Z0-9_-]+:.*##/ {printf "%-25s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

tree: ## Affiche la structure du repo (hors dossiers techniques)
	tree -I 'node_modules|.git|dist|build|venv|__pycache__|dbt_utils|target'

# ========== Environnement Python ==========
env-setup: ## Crée le virtualenv (.venv) et installe les dépendances Python
	@test -d $(VENV) || python -m venv $(VENV)
	$(PIP) install -r requirements.txt

env-lock: env-setup ## Gèle les versions des dépendances dans requirements.lock
	$(PIP) freeze > requirements.lock

env-clean: ## Supprime complètement le virtualenv (.venv)
	rm -rf $(VENV)

env-activate: ## Affiche la commande à exécuter pour activer le virtualenv
	@echo "To activate:"
	@echo "  source $(VENV)/bin/activate"

# ========== API & Ingestion ==========
api-check: ## Teste l’API Météo-France et les scripts de fetch (arguments : DEPT=<code>)
	$(PY) $(SCRIPT_FETCH) --list-stations --head 5
	$(PY) $(SCRIPT_FETCH) --dept $(DEPT) --head 5

dwh-ingest: ## Ingestion des données brutes dans DuckDB pour un département (arguments : DEPT=<code>)
	$(PY) -m $(MODULE_WRITE) --dept $(DEPT)

# ========== DuckDB ==========
dwh-tables: ## Liste les tables et schémas présents dans le warehouse DuckDB
	$(DUCKDB) $(DBPATH) -c "SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name;"

dwh-table-info: ## Affiche la définition des colonnes pour une table (argument : TABLE=<schema.table>)
	$(DUCKDB) $(DBPATH) -c "PRAGMA table_info('$(TABLE)');"

dwh-table-shape: ## Affiche le nombre de lignes et de colonnes pour une table (argument : TABLE=<schema.table>)
	$(DUCKDB) $(DBPATH) -c "WITH s AS ( \
	  SELECT \
	    (SELECT COUNT(*) FROM $(TABLE)) AS nrows, \
	    (SELECT COUNT(*) FROM pragma_table_info('$(TABLE)')) AS ncols \
	) \
	SELECT nrows, ncols FROM s;"
	
dwh-table-sample: ## Affiche un extrait de la table pour inspection rapide (argument : TABLE=<schema.table>)
	$(PY) scripts/utils/peek_duckdb.py --table $(TABLE)

dwh-table: dwh-table-shape dwh-table-info dwh-table-sample ## Résumé complet d’une table : shape + info colonnes + sample (argument : TABLE=<schema.table>)

dwh-reset: ## Réinitialise les schémas calculés (staging, intermediate, marts) en conservant le raw
	@echo "🧹 Cleaning warehouse (keeping raw)..."
	@echo "DROP SCHEMA IF EXISTS staging CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS intermediate CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS marts CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "✅ Warehouse reset complete."

# ========== DBT ==========
dbt-build: ## Exécute dbt deps puis dbt run sur le projet
	$(DBT) deps
	$(DBT) run

dbt-test: ## Exécute la suite de tests dbt
	$(DBT) test

dbt-rebuild: ## Full refresh (reset + deps + run --full-refresh + test)
	@$(MAKE) dwh-reset
	$(DBT) deps
	$(DBT) run --full-refresh
	$(DBT) test
	@echo "✅ DBT full refresh complete."

# ========== Sources DBT ==========
dbt-sources-test: ## Lance les tests dbt sur les sources
	$(DBT) test --select "source:*"

dbt-sources-freshness: ## Vérifie la fraîcheur des sources
	$(DBT) source freshness

dbt-sources-check: dbt-sources-test dbt-sources-freshness ## Combo sur les sources: Tests & Fraîcheur

# ========== Documentation DBT ==========
dbt-docs-generate: ## Génère la documentation HTML dbt dans target/
	$(DBT) docs generate

dbt-docs-serve: ## Sert la doc dbt en local (http://localhost:8080)
	$(DBT) docs serve --port 8080

dbt-docs: dbt-docs-generate dbt-docs-serve ## Génère puis sert la doc dbt en local (http://localhost:8080)

# ========== Lint ==========
py-lint: ## Lint Python
	$(VENV)/bin/ruff check .

py-fmt: ## Format Python
	$(VENV)/bin/ruff format .

sql-lint: ## Lint SQL
	$(VENV)/bin/sqlfluff lint $(DBT_PROJECT)

sql-fmt: ## Format SQL
	$(VENV)/bin/sqlfluff fix $(DBT_PROJECT) --rules LT08,LT09,LT10,LT12,AL01,LT02
