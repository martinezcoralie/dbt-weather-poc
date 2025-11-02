# Makefile minimal — dbt-weather-poc
VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
SCRIPT_FETCH=scripts/ingestion/fetch_meteofrance_paquetobs.py
MODULE_WRITE=scripts/ingestion/write_duckdb_raw

STATION?=01014002   # 8 chiffres, ?= utilise la valeur seulement si elle n’a pas déjà été fournie par l’utilisateur
DEPT?=75

.PHONY: venv install lock smoke clean write clean-db peek

venv: # test -d $(VENV) → vérifie si le dossier $(VENV) existe.
	@test -d $(VENV) || python -m venv $(VENV) 

install: venv
	$(PIP) install -r requirements.txt

lock: venv
	$(PIP) install -r requirements.txt
	$(PIP) freeze > requirements.lock

smoke: stations sixmin hourly
	$(PY) $(SCRIPT_FETCH) --list-stations --head 5
	$(PY) $(SCRIPT_FETCH) --station $(STATION) --head 5
	$(PY) $(SCRIPT_FETCH) --dept $(DEPT) --head 5

clean:
	rm -rf $(VENV)

write: venv
	$(PY) -m $(MODULE_WRITE) --dept $(DEPT)

clean-db:
	rm -f warehouse.duckdb

peek: venv
	$(PY) scripts/utils/peek_duckdb.py
