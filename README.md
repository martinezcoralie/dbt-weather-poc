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

Voir la documentation détaillée dans [`docs/ingestion.md`](docs/ingestion.md).

Commande principale :

```bash
make dwh-ingest DEPT=9
```

---

## 🧩 Modélisation dbt

Vue d’ensemble dans [`docs/dbt.md`](docs/dbt.md).

Commandes clés :

```bash
make dbt-build
make dbt-test
make dbt-rebuild
```

---

## 📚 Documentation dbt

Documentation détaillée dans [`docs/dbt-docs.md`](docs/dbt-docs.md).

---

## 🔎 Inspection du DataWarehouse (DuckDB)

Détails et commandes dans [`docs/warehouse.md`](docs/warehouse.md).

---

## 📊 Dashboard Streamlit (exposure dbt)

Détails d’usage et exposition dans [`docs/dashboard.md`](docs/dashboard.md).

---

## 🧰 Makefile

Toutes les commandes du projet sont disponibles via **Makefile** :

```bash
make help
```

---

## Scope & limites

Ce projet :

* ne vise pas à produire une BI métier aboutie,
* n’embarque pas (encore) d’orchestration ni CI/CD cloud,
* sert d’exemple pédagogique pour démontrer la maîtrise dbt.

---

## Prochaines évolutions

* CI/CD (tests + docs + artefacts)
* Amélioration du dashboard (UX & insights métier)

---

## 👤 Auteur

Coralie Martinez