# Makefile — dbt-weather-poc
VENV := .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip

# Ingestion scripts/modules
SCRIPT_FETCH  := scripts/ingestion/fetch_meteofrance_paquetobs.py
MODULE_WRITE  := scripts.ingestion.write_duckdb_raw

# DB / Tools
DBPATH  := warehouse.duckdb
DUCKDB  := duckdb
DBT     := dbt

# Params (overridable: `make write DEPT=09`)
STATION ?= 01014002
DEPT    ?= 9

.PHONY: venv install lock smoke clean write peek show-db reset-db rebuild

venv:
	@test -d $(VENV) || python -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

lock: venv
	$(PIP) install -r requirements.txt
	$(PIP) freeze > requirements.lock

clean:
	rm -rf $(VENV)

smoke:
	$(PY) $(SCRIPT_FETCH) --list-stations --head 5
	$(PY) $(SCRIPT_FETCH) --station $(STATION) --head 5
	$(PY) $(SCRIPT_FETCH) --dept $(DEPT) --head 5

write: venv
	$(PY) -m $(MODULE_WRITE) --dept $(DEPT)

peek: venv
	$(PY) scripts/utils/peek_duckdb.py

show-db:
	$(DUCKDB) $(DBPATH) -c "SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name;"

# --- Reset des schémas calculés (on garde raw/*) ---
reset-db:
	@echo "🧹 Cleaning warehouse (keeping raw)..."
	@echo "DROP SCHEMA IF EXISTS staging CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS intermediate CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "DROP SCHEMA IF EXISTS marts CASCADE;" | $(DUCKDB) $(DBPATH)
	@echo "✅ Warehouse reset complete."

# --- Rebuild complet DBT (full-refresh) après reset ---
rebuild:
	@$(MAKE) reset-db
	@echo "🏗️ Running full DBT build..."
	@$(DBT) deps
	@$(DBT) run --full-refresh
	@$(DBT) test
	@echo "✅ DBT full refresh complete."
