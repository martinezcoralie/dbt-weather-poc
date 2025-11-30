# 🌤️ dbt-weather-poc

Pipeline analytique Météo-France — ingestion, historisation et modélisation de données horaires — basé sur **Python**, **DuckDB**, **dbt** et **Streamlit**.

Ce projet a un objectif simple : **démontrer, de bout en bout, la maîtrise d’un workflow moderne dbt**, depuis la collecte des données jusqu’à leur exposition en BI.

---

## Ce que ce projet met en œuvre côté dbt

Ce repository illustre concrètement :

* **Sources déclarées** avec contrôle de fraîcheur (`loaded_at_field`)
* **Tests dbt** : not_null, unique, relationships, contraintes métier, tests génériques
* **Contrats de schéma** sur les modèles critiques
* **Organisation modulaire** : `staging → intermediate → marts`
* **Modèles incrémentaux** (stratégie `merge`)
* **Macros personnalisées** (features météo, conversions, casts, time series analysis)
* **Seeds** (échelle de Beaufort)
* **Exposures** (dashboard Streamlit comme consommateur final)
* **Documentation dbt** (descriptions, docs blocks, lineage graph)
* **Facteurs métier** : dimensions stations & vent, table de faits horaire
* **Publication automatique de la documentation dbt** (GitHub Actions + GitHub Pages)

L’objectif n’est pas la BI en tant que produit, mais **la démonstration des bonnes pratiques dbt dans un pipeline réaliste**.

---

## Architecture globale

```text
Météo-France API
    ↓
Ingestion Python
    ↓
DuckDB (raw.*)
    ↓
dbt (staging → intermediate → marts)
    ↓
Dashboard Streamlit (exposure)
```
---

## Stack technique

- **Python 3.12** — ingestion & utilitaires
- **dbt-core + dbt-duckdb** — transformation & tests
- **DuckDB (CLI + lib Python)** — data warehouse local
- **Streamlit** — exposition BI
- **Pandas / PyArrow** — manipulation de données
- **SQLFluff / Ruff** — linting SQL & Python
- **GitHub Actions** — génération et déploiement automatique des docs dbt (CI) + build dbt avec ingestion API

---

## 🚀 Mise en route

### 1) Installer l’environnement

```bash
make env-setup
```

### 2) Activer l’environnement

```bash
source .venv/bin/activate
```

### 3) Variables d’environnement

Créer `.env` :

```bash
METEOFRANCE_TOKEN=xxxxxxxxxxxx
DUCKDB_PATH=data/warehouse.duckdb
```

avec :
- `METEOFRANCE_TOKEN` : la clé API Météo-France  
- `DUCKDB_PATH` : le chemin du fichier DuckDB (par défaut `data/warehouse.duckdb`)

### 4) Activer le profil dbt

```bash
export DBT_PROFILES_DIR=./profiles
```

---

## 📥 Ingestion (API → DuckDB)

```bash
make dwh-ingest DEPT=9
```

Résultat attendu :
- données brutes dans `raw.obs_hourly` et `raw.stations`
- pas de transformation / typage
- déduplication automatique

👉 Documentation détaillée : [`docs/ingestion.md`](docs/ingestion.md).

---

## 🧩 Modélisation dbt

Commandes principales :

```bash
make dbt-build
make dbt-test
make dbt-rebuild
```

À retenir :
- `staging` = nettoyage + typage
- `intermediate` = calculs métier (features météo)
- `marts` = faits + dimensions

👉 Documentation détaillée : [`docs/dbt.md`](docs/dbt.md).

---

## 📚 Documentation dbt

### Accès local

```bash
make dbt-docs-generate
make dbt-docs-serve
```

Accès local : [http://localhost:8080](http://localhost:8080)

👉 Documentation détaillée : [`docs/dbt-docs.md`](docs/dbt-docs.md).

### Documentation en ligne (CI GitHub Actions)

Une GitHub Action génère et déploie automatiquement la documentation dbt sur GitHub Pages à chaque push sur `main` :

👉 [https://martinezcoralie.github.io/dbt-weather-poc/](https://martinezcoralie.github.io/dbt-weather-poc/)


### Aperçu de la documentation dbt

#### Navigation dans dbt Docs
L’interface permet d’explorer facilement l’ensemble des modèles, sources, tests et descriptions.

<img src="docs/images/dbt_sidebar.png" width="150">


#### Fiche d’un modèle analytique (`fct_obs_hourly`)
Chaque modèle documenté expose sa description, ses colonnes, ses contraintes et ses tests associés.

<img src="docs/images/dbt_table_extract.png" width="250">


#### Lineage complet (raw → staging → intermediate → marts)
Le lineage graph permet de visualiser le flux de transformation de bout en bout, jusqu’à la consommation BI.

![lineage graph](docs/images/lineage-graph.png)

---

## 🔎 Inspection du DataWarehouse (DuckDB)

Exemples utiles :

```bash
make dwh-tables
make dwh-table-info TABLE=raw.stations
```

👉 Documentation détaillée : [`docs/warehouse.md`](docs/warehouse.md).

---

## 📊 Dashboard Streamlit (exposure dbt)

Lancer l’app :

```bash
streamlit run apps/bi-streamlit/app.py
```

URL : http://localhost:8501

👉 Documentation détaillée : [`docs/dashboard.md`](docs/dashboard.md).

---

## 🧰 Makefile

Toutes les commandes du projet sont disponibles via **Makefile** :

```bash
make help
```

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

## Scope & limites

Ce projet :

* ne vise pas à produire une BI métier aboutie,
* embarque une première CI (build + déploiement des docs dbt), mais pas encore d’orchestration ni CI/CD complète du pipeline,
* sert d’exemple pédagogique pour démontrer la maîtrise dbt.

---

## Prochaines évolutions

* Étendre la CI/CD au reste du pipeline (tests, artefacts, éventuels déploiements)
* Amélioration du dashboard (UX & insights métier)

---

## 👤 Auteur

Coralie Martinez