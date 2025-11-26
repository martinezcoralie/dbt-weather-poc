
# 🌤️ dbt-weather-poc

Pipeline analytique Météo-France — ingestion, historisation et modélisation de données horaires — basé sur **Python**, **DuckDB**, **dbt** et **streamlit**.

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

```
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
- 
### 4) Activer le profil dbt

```bash
export DBT_PROFILES_DIR=./profiles
```

---

## Ingestion des données (API → DuckDB)

### Lancer une ingestion départementale
```bash
make dwh-ingest DEPT=75
```
**Ce que fait la commande :**

* crée `warehouse.duckdb` si absent ;
* interroge l’API Météo-France (dernières **24 h**) pour le département `DEPT` ;
* écrit en **brut** dans `raw.stations` et `raw.obs_hourly`.

**Garantie de “raw” :**

* ✅ Noms de colonnes **strictement identiques** à la source (aucun renommage, aucun `lower/strip`)
* ✅ Types **inchangés** (strings le cas échéant)
* ✅ Aucune normalisation d’unités / sémantique (fait plus tard en **staging dbt**)
* ➕ Champs ajoutés par l’ingestion : `load_time` (UTC) et `dept_code`

**Idempotence & déduplication :**

* Les doublons sont empêchés via la clé logique
  `(validity_time, geo_id_insee, reference_time)` : seules les lignes nouvelles sont ajoutées.

---

### Mesurer la fraîcheur des sources dans le datawarehouse DuckDB

```bash
make dbt-sources-freshness
```

**Comment ça marche :**

* dbt lit `loaded_at_field: load_time` (défini dans `sources.yml`)
* compare `load_time` à l’horloge actuelle, et applique les seuils :

  * ⚠️ **warn** si `load_time` > **2 h** 
    * données en retard (surveillance conseillée)
  * ⛔ **error** si `load_time` > **4 h**
    * pipeline considéré **en échec**
  *  ✅ **pass** sinon
     *  la source est à jour

**Que faire en cas d’alerte/erreur ?**

1. Relancer l’ingestion :

   ```bash
   make dwh-ingest DEPT=9
   ```
2. Vérifier le token API et la connectivité réseau.

---

### Exécuter les tests sources

```bash
make dbt-sources-test
```
Les tests effectuées sont ceux déclarés dans `sources.yml`.

---

## 🔎 Inspection du DataWarehouse (DuckDB)

### Lister l'ensemble des tables
```bash
make dwh-tables
```
Cela permet de visualiser les schemas et noms de toutes les tables du DataWarehouse.

### Afficher les colonnes d'une table
```bash
make dwh-table-info TABLE=raw.stations
```
Cela permet de visualiser les noms des colonnes de la table `TABLE` et leur type.

### Afficher un extrait d'une table
```bash
make dwh-table-sample TABLE=raw.stations
```
Permet de visualiser un extrait des données de la table `TABLE` directement dans le terminal.

### Afficher les dimensions d'une table
```bash
make dwh-table-shape TABLE=raw.stations
```
Permet de visualiser le nombre de lignes et de colonnes de la table `TABLE`.

### Afficher toute les infos d'une table
```bash
make dwh-table TABLE=raw.stations
```
Permet de visualiser colonnes + dimensions + extrait de la table `TABLE`.

### Explorer le warehouse avec DuckDB CLI

#### Installation du client DuckDB
```bash
brew install duckdb
```

#### Ouvrir le shell interactif
```bash
duckdb warehouse.duckdb
```

#### Commandes utiles
```sql
show;                                  -- liste les tables
select count(*) from raw.stations;     -- compte les lignes d'une table
select * from raw.obs_hourly limit 5;  -- aperçu des données
show raw.stations;                     -- affiche le schéma d'une table
```

---

## 🧩 Modélisation dbt

### Structure

* `staging` : nettoyage, typage, renommage clair
* `intermediate` : calculs intermédiaires, features météo
* `marts` : tables analytiques et dimensionnelles

### Modèles clés

* **`fct_obs_hourly`** (table de faits horaire)
* **`dim_stations`** (dimension géographique des stations)

### Modèles incrémentaux

Deux modèles utilisent `materialized: incremental` avec stratégie `merge`
pour éviter un full refresh systématique.

Forcer un rebuild complet :

```bash
make dbt-rebuild
```

---

## ⚙️ dbt — exécution par actions

### 1) Tester la connexion au DWH
```bash
dbt debug
```

### 2) Lancer l’exécution de tous les modèles
```bash
make dbt-build     # deps + run
```

### 2.bis) Exécuter un sous-ensemble de modèles

```bash
dbt run --select stg_obs_hourly      # un modèle
dbt run --select tag:stg     # tous les modèles ayant le tag `stg`
dbt run --full-refresh -s tag:int # full refresh ciblé
```

### 3) Lancer les tests

```bash
make dbt-test    # tous les tests
dbt test -s tag:mart  # tous les modèles ayant le tag `mart`
```

### 4) Lancer un rebuild complet

```bash
make dbt-rebuild    # reset + deps + run --full-refresh + test
```

---

## 📚 Documentation dbt

Une fois les modèles exécutés (`make dbt-rebuild`), on peut générer et explorer la
documentation dbt (modèles, sources, tests, lineage).

### Générer la documentation

```bash
make dbt-docs-generate
```

Cela crée les fichiers HTML/JSON de documentation dans le dossier `target/`.

### Servir la documentation en local

```bash
make dbt-docs-serve
```

Puis ouvrir le navigateur sur :

* [http://localhost:8080](http://localhost:8080)

On y retrouve :

* la liste des sources et modèles (staging, intermediate, marts) ;
* les descriptions de tables et de colonnes définies dans les fichiers YAML ;
* les tests associés ;
* le **graph de lineage** permettant de visualiser le flux `raw → staging → intermediate → marts`. Accessible via le bouton « Lineage » en bas à droite du panneau dbt Docs : <img src="docs/images/lineage-graph-icon.png" width="50">


---

## 📊 Dashboard Streamlit (exposure dbt)

Une fois les données ingérées et les modèles dbt exécutés, on peut explorer les marts via une petite app Streamlit.

### Lancer le dashboard

```bash
streamlit run apps/bi-streamlit/app.py
```

URL par défaut :
[http://localhost:8501](http://localhost:8501)

Ce dashboard s'appuie sur :
* `fct_obs_hourly`

### Exposure associé

Le dashboard est déclaré comme **exposure dbt** (`weather_bi_streamlit`), permettant de :

* cibler uniquement les modèles qui l’alimentent :

  ```bash
  dbt ls -s +exposure:weather_bi_streamlit
  ```
* exécuter uniquement ce périmètre :

  ```bash
  dbt run -s +exposure:weather_bi_streamlit
  dbt test -s +exposure:weather_bi_streamlit
  ```

---

## 🧰 Makefile

Toutes les commandes du projet sont disponibles via **Makefile** :

```bash
make help
```

---

## 🧱 Scope & limites

Ce projet :

* ne vise pas à produire une BI métier aboutie,
* n’embarque pas (encore) d’orchestration ni CI/CD cloud,
* sert d’exemple pédagogique pour démontrer la maîtrise dbt.

---

## 🔭 Prochaines évolutions

* Snapshots (SCD2 sur `dim_stations`)
* CI/CD (tests + docs + artefacts)
* Migration cloud (BigQuery / Snowflake / Postgres managé)
* Amélioration du dashboard (UX & insights métier)

---

## 👤 Auteur

Coralie Martinez

---

## Annexes

### 🧰 Scripts ingestion

#### `scripts/ingestion/fetch_meteofrance_paquetobs.py`

Client fetch-only :
- Appels API `/liste-stations` et `/paquet/horaire`
- Parsing CSV **sans aucune transformation**
- Retourne des DataFrames RAW

#### `scripts/ingestion/write_duckdb_raw.py`

Writer vers DuckDB :
- création du schéma `raw`
- `load_time` et `dept_code` ajoutés
- déduplication sur PK logique

---

**Auteur :** Coralie Martinez
