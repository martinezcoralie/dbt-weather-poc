# dbt-weather-poc

**PoC Météo :** ingestion des données Météo-France (API Paquet Observations) vers DuckDB (`raw.*`).

### 💡 Objectif

* Démontrer un flux de données **API → Warehouse → dbt** portable (DuckDB → Redshift/BigQuery/Snowflake).
* Base pour un **portfolio freelance** : code clair, testé, documenté.

---

### 🛠️ Installation (dev local)

```bash
make install
```

### 🔧 Ingestion (API → DuckDB)

```bash
make write DEPT=75
```

* Crée `warehouse.duckdb`
* Tables : `raw.stations`, `raw.obs_hourly`

### 🔍 Inspection rapide

```bash
make peek
```

### 🗑️ Nettoyer

```bash
make clean-db
```

---

### 🔢 Naviguer dans le warehouse (CLI DuckDB)

#### Installer le client DuckDB CLI

**macOS**

```bash
brew install duckdb
```

#### Ouvrir le shell interactif

```bash
duckdb warehouse.duckdb
```

#### Commandes utiles
Dans le shell interactif DuckDB :
```sql
show;                                 -- liste les tables disponibles
select count(*) from raw.stations;      -- compte les lignes d'une table
select * from raw.obs_hourly limit 5;   -- aperçu des données
show raw.stations;                      -- affiche le schéma d'une table
```

---

### 📊 Prochaines étapes

* Ajouter `dbt_project.yml` + modèles `stg_*/int_*/mart_*`
* Configurer CI (`dbt build`, tests, docs)
* Publier artefacts (docs/lineage)

---

**Auteur :** Coralie
