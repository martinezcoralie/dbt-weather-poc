# Vue d’ensemble

Projet dbt + DuckDB autour des données horaires Météo-France. Objectif : démontrer des pratiques dbt pro (tests, contrats, macros, incrémental, exposures), une ingestion maîtrisée, une exposition BI Streamlit, une CI (build + docs), et une orchestration locale Prefect.

## Ce que le projet met en œuvre
- **Sources déclarées** avec fraîcheur (`loaded_at_field`).
- **Tests dbt** (intégrité + métier) et **contrats de schéma** sur les modèles critiques.
- **Layering** `staging → intermediate → marts` avec **modèles incrémentaux** (merge).
- **Macros métiers** (features météo, conversions, time series) et **seeds** (échelle de Beaufort, intensités).
- **Exposure** pour le dashboard Streamlit.
- **Documentation dbt** (descriptions, docs blocks, lineage) publiée automatiquement (Pages).
- **Orchestration Prefect** horaire ingestion → dbt.

## Pourquoi cela compte pour un client / recruteur
- Données réelles (API Météo-France) et pipeline reproductible.
- Qualité dbt : tests, contrats, macros, incrémental, seeds, exposure.
- BI concrète (Streamlit) connectée aux marts dbt.
- CI qui rejoue ingestion + dbt build et publie la doc.
- Orchestration légère démontrant l’intégration autour de dbt.

## Stack
- Python 3.12 (ingestion, orchestration)
- DuckDB
- dbt-core + dbt-duckdb
- Streamlit
- SQLFluff / Ruff
- GitHub Actions (build dbt + docs)
- Prefect 3


---
## Parcours dev local (sans Docker)
```bash
git clone https://github.com/martinezcoralie/dbt-weather-poc.git
cd dbt-weather-poc
```

### 1. Installer l’environnement

```bash
make env-setup
source .venv/bin/activate
```

### 2. Variables d’environnement

Créer un fichier `.env` :

```bash
METEOFRANCE_TOKEN=xxxxxxxxxxxx
DUCKDB_PATH=data/warehouse.duckdb
```
avec `METEOFRANCE_TOKEN` la clé API Météo-France et `DUCKDB_PATH` le chemin du fichier DuckDB.

### 3. Activer le profil dbt

```bash
export DBT_PROFILES_DIR=./profiles
```

### 4. Ingestion brute (API → DuckDB)

```bash
make dwh-ingest DEPT=9
```

Résultat attendu :
- données brutes dans `raw.obs_hourly` et `raw.stations`
- pas de transformation / typage
- déduplication automatique

👉 Documentation détaillée : [`ingestion.md`](ingestion.md).

### 5. Modélisation dbt

```bash
make dbt-build
```

---

## 🧩 Modélisation dbt (vue détaillée)

Points clés du projet dbt :

* **Layering clair** :

  * `staging` = nettoyage + typage,
  * `intermediate` = calculs métier (features météo, agrégations),
  * `marts` = tables de faits et dimensions analytiques.
* **Qualité** :

  * tests génériques (intégrité, clés, relations),
  * tests métier (plages de valeurs, non-négativité, etc.),
  * contrats de schéma sur les modèles exposés.
* **Performance & maintenabilité** :

  * modèles incrémentaux pour limiter les coûts de recalcul,
  * macros pour mutualiser les conversions, features météo et logiques temporelles.

👉 Documentation détaillée : [`dbt.md`](dbt.md).

---

## 📚 Documentation dbt

### Local

```bash
make dbt-docs-generate
make dbt-docs-serve
```

Accès : [http://localhost:8080](http://localhost:8080)

### Hébergée (CI → GitHub Pages)

Une GitHub Action génère et déploie automatiquement la documentation dbt à chaque push sur `main` (build + upload artefact, puis publication sur Pages) :

- Accès : [https://martinezcoralie.github.io/dbt-weather-poc/](https://martinezcoralie.github.io/dbt-weather-poc/)

👉 Documentation détaillée : [`dbt-docs.md`](dbt-docs.md).

---

## 📊 Dashboard Streamlit (exposure dbt)

Lancer le dashboard :

```bash
make app
```

Accès : [http://localhost:8501](http://localhost:8501)

Le dashboard consomme les marts dbt stockés dans DuckDB (dimensions de stations, échelle de Beaufort, faits horaires).

👉 Détails : [`dashboard.md`](dashboard.md).

---


## ✅ CI dbt (build + API Météo-France)

Une CI GitHub Actions rejoue une partie du pipeline à chaque push / PR sur `main` :

- ingestion des données brutes depuis l’API Météo-France via `make dwh-ingest DEPT=9`,
- création d’un warehouse DuckDB local dans l’environnement CI,
- exécution de `dbt deps` puis `dbt build` avec `DBT_PROFILES_DIR=./profiles`.

La CI s’appuie sur :

- un secret GitHub Actions `METEOFRANCE_TOKEN` (clé API Météo-France),
- une variable d’environnement `DUCKDB_PATH` pointant vers `data/warehouse.duckdb`.

Ce choix permet de tester les modèles dbt et leurs tests métier sur des données réelles, sans versionner les données Météo-France dans le dépôt.

---


## ⚙️ Orchestration locale (Prefect — bonus)

Une orchestration locale est mise en place avec **Prefect 3** :

* un flow `weather_hourly_pipeline` orchestre :

  * l’ingestion (API → DuckDB),
  * puis `dbt build`,
* un deployment Prefect avec schedule horaire pilote l’exécution régulière du pipeline tant que le serveur Prefect et le process de service tournent.

Cette orchestration est volontairement légère : elle sert à montrer comment **plugger un orchestrateur moderne autour d’un projet dbt existant**, sans complexifier le cœur du repo.

👉 Détails : [`orchestration.md`](orchestration.md).

---

## 🧰 Commandes (Makefile)

Toutes les commandes (ingestion, dbt, docs, utilitaires DuckDB, lint, etc.) sont centralisées dans le **Makefile** :

```bash
make help
```

---

## Scope & limites

Ce projet :

* est centré sur la **démonstration de bonnes pratiques dbt** (structure, tests, contrats, docs, exposures),
* embarque une CI et une orchestration locale pour illustrer l’intégration de dbt dans un pipeline complet,
* **ne vise pas** (dans cette version) :

  * un déploiement 24/7 sur une infra cloud,
  * une BI métier aboutie.

---

## Prochaines évolutions

* Étendre la CI/CD (artefacts, checks supplémentaires, éventuels déploiements),
* Déployer pipeline + dashboard sur une infra cloud (VM / containers),
* Approfondir l’orchestration (Prefect Cloud / autre orchestrateur) si besoin projet.

---

## 👤 Auteur

Coralie Martinez
