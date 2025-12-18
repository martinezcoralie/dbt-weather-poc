# 🌤️ dbt-weather-poc — Pipeline météo (dbt + DuckDB)

Pipeline analytique de bout en bout autour des données horaires Météo-France :
**ingestion Python → DuckDB (raw) → dbt (staging/intermediate/marts) → Streamlit (BI)**,
avec une orchestration locale optionnelle via **Prefect**.

Objectif : démontrer un **workflow dbt** moderne (layering, tests, contrats, macros, incremental, docs, exposure)
dans un cas réel et reproductible.

## Ce que ce projet démontre

TODO

## Architecture
```text
Météo-France API
  ↓ (ingestion Python)
DuckDB (raw.*)
  ↓ (modélisation dbt)
DuckDB (staging → intermediate → marts)
  ↓
Streamlit (dashboard)

+ optionnel : Prefect pour planifier ingestion + dbt
```

👉 Pour plus de détails sur chaque brique, voir la documentation complémentaire (TODO: mettre lien vers la section ci bas).

---

## 🚀 Démo rapide (pull d'une image Docker)
Cette image permet d'ouvrir le dashboard Streamlit sur un warehouse DuckDB de démonstration (pas de token requis).

```bash
# Pull de l’image

docker pull dbt-weather-poc/weather-app:latest 


# Lancer le conteneur Streamlit sur le DuckDB démo

docker run --rm -p 8501:8501 dbt-weather-poc/weather-app:latest make app VENV=system 
```
Ouvrir le dashboard [http://localhost:8501](http://localhost:8501).

---

## Démo complète (via Docker Compose)

**Prérequis:**
* Docker Desktop (ou Docker CLI)
* Docker Compose v2 (inclus avec Docker Desktop)

```bash
git clone https://github.com/martinezcoralie/dbt-weather-poc.git
cd dbt-weather-poc
```

### (Optionel) Pour l'ingestion des données de l'API Météo-France

Créer un fichier `.env`
```bash
cp .env.example .env
```

Renseigner la clé API Météo-France (Voir [🔑 Obtenir une clé API Météo-France](meteofrance_token.md)) 
```env
METEOFRANCE_TOKEN=VotreCleIci
```

Lancer l'ingestion sur le département de votre choix
```bash
DEPT=9 docker compose --profile ingest run --rm ingest
```

### Pour exécuter la modélisation dbt (stg->int->marts)


```bash
docker compose --profile build run --rm dbt
```

Si vous aviez ingéré de nouvelles données, alors ... sinon, cela rejoue dbt build sur la base démo.

### Pour lancer le dashboard Streamlit

```bash
# Lancer le conteneur (Streamlit)

docker compose up app 
```
Ouvrir [http://localhost:8501](http://localhost:8501).


### Pour lancer l'orchestration Prefect du pipeline (ingestion->modélisation)

Pré-requis : `.env` avec `METEOFRANCE_TOKEN` ([🔑 Obtenir une clé API Météo-France](meteofrance_token.md)).

```bash
docker compose --profile prefect up -d prefect-server prefect # Démarre Prefect (UI + worker/serve)

```

Ouvrir l’UI Prefect [http://localhost:4200](http://localhost:4200).
Vous verrez les runs programmés, réalisés, etc... TODO améliorer
Vous verrez l'app Streamlit se mettre à jour une fois par heure (TODO améliorer)


### Pour faire un reset complet (reseed du warehouse démo)

```bash
docker compose down -v
```

---

## Parcours dev local (sans Docker)
Pré-requis : 
- 🔑 Obtenir une clé API Météo-France](meteofrance_token.md)

```bash
git clone https://github.com/martinezcoralie/dbt-weather-poc.git
cd dbt-weather-poc

# Installer l’environnement
make env-setup
source .venv/bin/activate

# Activer le profil dbt
export DBT_PROFILES_DIR=./profiles

# Toutes les commandes
make help

# Ingestion brute (API → DuckDB)
make dwh-ingest DEPT=9

# Modélisation dbt
make dbt-build

# Documentation dbt
make dbt-docs-generate
make dbt-docs-serve # (http://localhost:8080)

Dashboard Streamlit (exposure dbt)

# Lancer le dashboard :
make app
```


---

## 📎 Documentation complémentaire

La documentation détaillée du projet est organisée par brique :

- [`docs/overview.md`](docs/overview.md) — XXX
- [`docs/meteofrance_token.md`](docs/meteofrance_token.md) - comment récupérer une clé API Météo-France (c'est gratuit!)
- [`docs/ingestion.md`](docs/ingestion.md) — ingestion API Météo-France → DuckDB (`raw.*`)
- [`docs/warehouse.md`](docs/warehouse.md) — commandes pour explorer le warehouse DuckDB
- [`docs/dbt.md`](docs/dbt.md) — structure des modèles dbt, layering et incrémental
- [`docs/dbt-docs.md`](docs/dbt-docs.md) — génération et exploration de dbt Docs (lineage, tests, modèles)
- [`docs/dashboard.md`](docs/dashboard.md) — dashboard Streamlit (exposure dbt)
- [`docs/orchestration.md`](docs/orchestration.md) — orchestration locale du pipeline avec Prefect