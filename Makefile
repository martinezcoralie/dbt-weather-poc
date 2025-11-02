# Makefile minimal — dbt-weather-poc
VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
SCRIPT_FETCH=scripts/ingestion/fetch_meteofrance_paquetobs.py

STATION?=01014002   # 8 chiffres, ?= utilise la valeur seulement si elle n’a pas déjà été fournie par l’utilisateur
DEPT?=75

.PHONY: venv install lock smoke stations sixmin hourly clean

venv: # test -d $(VENV) → vérifie si le dossier $(VENV) existe.
	@test -d $(VENV) || python -m venv $(VENV) 

install: venv
	$(PIP) install -r requirements.txt

lock: venv
	$(PIP) install -r requirements.txt
	$(PIP) freeze > requirements.lock

stations: venv
	$(PY) $(SCRIPT_FETCH) --list-stations --head 5

sixmin: venv
	$(PY) $(SCRIPT_FETCH) --station $(STATION) --head 5

hourly: venv
	$(PY) $(SCRIPT_FETCH) --dept $(DEPT) --head 5

smoke: stations sixmin hourly

clean:
	rm -rf $(VENV)
