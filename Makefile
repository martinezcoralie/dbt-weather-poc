# Makefile — dbt-weather-poc
# Usage: make <cible> (ex : make ingest DEPT=9)

# ========== Configuration ==========
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

# Par défaut on garde .venv, mais on peut le surcharger
VENV ?= .venv
# Si VENV est "system", on utilise directement python/pip/dbt du système
ifeq ($(VENV),system)
    PY := python
    PIP := pip
    DBT := dbt
    PREFECT := prefect
	STREAMLIT := streamlit
    RUFF := ruff
    SQLFLUFF := sqlfluff
else
    PY := $(VENV)/bin/python
    PIP := $(VENV)/bin/pip
    DBT := $(VENV)/bin/dbt
    PREFECT := $(VENV)/bin/prefect
    STREAMLIT := $(VENV)/bin/streamlit
    RUFF := $(VENV)/bin/ruff
    SQLFLUFF := $(VENV)/bin/sqlfluff
endif

# Options dbt additionnelles (surchage possible : DBT_FLAGS="...")
DBT_FLAGS ?=

# Si on est dans un conteneur Docker, on désactive partial parsing
IN_DOCKER := $(shell test -f /.dockerenv && echo 1 || echo 0)
ifeq ($(IN_DOCKER),1)
  DBT_FLAGS += --no-partial-parse
endif

DUCKDB := duckdb

# Scripts et modules ingestion
MODULE_FETCH  := scripts.ingestion.fetch_meteofrance_paquetobs
MODULE_WRITE  := scripts.ingestion.ingest_duckdb

# Chemins
DUCKDB_PATH ?= data/warehouse.duckdb
export DUCKDB_PATH
DBT_PROJECT := .

# Prefect API
PREFECT_API_URL ?= http://127.0.0.1:4200/api
export PREFECT_API_URL

# Paramètres (overridable)
DEPT    ?= 9
TABLE   ?= raw.obs_hourly

.PHONY: help tree \
	env-setup env-clean env-activate \
	app \
	api-check \
	dwh-ingest dwh-reset dwh-tables \
	dwh-table-info dwh-table-shape dwh-table-sample dwh-table \
	dbt-build dbt-test dbt-rebuild \
	dbt-sources-test dbt-sources-freshness dbt-sources-check \
	dbt-docs-generate dbt-docs-serve dbt-docs \
	prefect-server prefect-ui flow-run flow-serve flow-status \
	py-lint py-fmt py-fmt-check py-check sql-lint sql-fmt

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

env-clean: ## Supprime complètement le virtualenv (.venv)
	rm -rf $(VENV)

env-activate: ## Affiche la commande à exécuter pour activer le virtualenv
	@echo "To activate:"
	@echo "  source $(VENV)/bin/activate"
	@echo "  export DBT_PROFILES_DIR=./configs/dbt"

# ========== BI app ==========
app: ## Lance le dashboard streamlit sur le port 8501
	streamlit run apps/bi-streamlit/app.py \
		--server.address 0.0.0.0 \
		--server.port 8501 \
		--browser.serverAddress localhost

# ========== API & Ingestion ==========
api-check: ## Teste l’API Météo-France et les scripts de fetch (arguments : DEPT=<code>)
	$(PY) -m $(MODULE_FETCH) --list-stations --head 5
	$(PY) -m $(MODULE_FETCH) --dept $(DEPT) --head 5

dwh-ingest: ## Ingestion des données brutes dans DuckDB pour un département (arguments : DEPT=<code>)
	$(PY) -m $(MODULE_WRITE) --dept $(DEPT)

# ========== DuckDB ==========
dwh-tables: ## Liste les tables et schémas présents dans le warehouse DuckDB
	$(DUCKDB) $(DUCKDB_PATH) -c "SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name;"

dwh-table-info: ## Affiche la définition des colonnes pour une table (argument : TABLE=<schema.table>)
	$(DUCKDB) $(DUCKDB_PATH) -c "PRAGMA table_info('$(TABLE)');"

dwh-table-shape: ## Affiche le nombre de lignes et de colonnes pour une table (argument : TABLE=<schema.table>)
	$(DUCKDB) $(DUCKDB_PATH) -c "WITH s AS ( \
	  SELECT \
	    (SELECT COUNT(*) FROM $(TABLE)) AS nrows, \
	    (SELECT COUNT(*) FROM pragma_table_info('$(TABLE)')) AS ncols \
	) \
	SELECT nrows, ncols FROM s;"
	
dwh-table-sample: ## Affiche un extrait de la table pour inspection rapide (argument : TABLE=<schema.table>)
	$(PY) scripts/duckdb/peek.py --table $(TABLE)

dwh-table: dwh-table-shape dwh-table-info dwh-table-sample ## Résumé complet d’une table : shape + info colonnes + sample (argument : TABLE=<schema.table>)

dwh-reset: ## Réinitialise les schémas calculés (staging, intermediate, marts) en conservant le raw
	@echo "🧹 Cleaning warehouse (keeping raw)..."
	@echo "DROP SCHEMA IF EXISTS staging CASCADE;" | $(DUCKDB) $(DUCKDB_PATH)
	@echo "DROP SCHEMA IF EXISTS intermediate CASCADE;" | $(DUCKDB) $(DUCKDB_PATH)
	@echo "DROP SCHEMA IF EXISTS marts CASCADE;" | $(DUCKDB) $(DUCKDB_PATH)
	@echo "✅ Warehouse reset complete."

# ========== DBT ==========
dbt-build: ## Exécute dbt deps puis dbt build sur le projet
	$(DBT) deps --project-dir $(DBT_PROJECT) $(DBT_FLAGS)
	$(DBT) build --project-dir $(DBT_PROJECT) $(DBT_FLAGS)

dbt-test: ## Exécute la suite de tests dbt
	$(DBT) test --project-dir $(DBT_PROJECT) $(DBT_FLAGS)

dbt-rebuild: ## Full refresh (reset + deps + build --full-refresh)
	@$(MAKE) dwh-reset
	$(DBT) deps --project-dir $(DBT_PROJECT) $(DBT_FLAGS)
	$(DBT) build --full-refresh --project-dir $(DBT_PROJECT) $(DBT_FLAGS)
	@echo "✅ DBT full refresh complete."

# ========== Sources DBT ==========
dbt-sources-test: ## Lance les tests dbt sur les sources
	$(DBT) test --select "source:*" --project-dir $(DBT_PROJECT) $(DBT_FLAGS)

dbt-sources-freshness: ## Vérifie la fraîcheur des sources
	$(DBT) source freshness --project-dir $(DBT_PROJECT) $(DBT_FLAGS)

dbt-sources-check: dbt-sources-test dbt-sources-freshness ## Combo sur les sources: Tests & Fraîcheur

# ========== Documentation DBT ==========
dbt-docs-generate: ## Génère la documentation HTML dbt dans target/
	$(DBT) docs generate --project-dir $(DBT_PROJECT) $(DBT_FLAGS)

dbt-docs-serve: ## Sert la doc dbt en local (http://localhost:8080)
	$(DBT) docs serve --port 8080 --project-dir $(DBT_PROJECT) $(DBT_FLAGS)

dbt-docs: dbt-docs-generate dbt-docs-serve ## Génère puis sert la doc dbt en local (http://localhost:8080)

# ========== Orchestration Prefect ==========
prefect-server: ## Démarre le serveur Prefect (UI http://localhost:4200)
	$(PREFECT) server start --host 0.0.0.0 --port 4200

prefect-ui: ## Ouvre l'UI Prefect locale dans le navigateur
	open http://localhost:4200

flow-run: ## Exécute le flow Prefect une fois (ingestion + dbt) pour DEPT=<code>
	$(PY) scripts/orchestration/flow_prefect.py --mode run --dept $(DEPT)

flow-serve: ## Lance le deployment Prefect horaire (cron) pour DEPT=<code>
	$(PY) scripts/orchestration/flow_prefect.py --mode serve --dept $(DEPT)

flow-status: ## Liste les deployments et les 5 derniers flow runs
	$(PREFECT) deployment ls
	$(PREFECT) flow-run ls --limit 5

# ========== Lint ==========
py-fix: ## Lint+format (modifie)
	$(RUFF) check . --fix
	$(RUFF) format .

py-check: ## Lint+format (CI, ne modifie pas)
	$(RUFF) check .
	$(RUFF) format --check .

sql-lint: ## Lint SQL
	$(SQLFLUFF) lint $(DBT_PROJECT)

sql-fmt: ## Format SQL
	$(SQLFLUFF) fix $(DBT_PROJECT) --rules LT08,LT09,LT10,LT12,AL01,LT02
