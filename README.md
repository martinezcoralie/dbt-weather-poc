# dbt-weather-poc

Pipeline d’ingestion et de modélisation Météo-France (Paquet Observations DPPaquetObs)  
Basé sur **DuckDB**, **Python**, et **dbt**.

> Ce projet DBT collecte et historise les observations météo horaires de Météo France pour le département de l’Ariège afin d’analyser la qualité de vie climatique selon les zones (soleil, humidité, vent, pluie).

## 💡 Objectifs

- Démontrer un flux de données complet **API → Warehouse → dbt**, portable et reproductible.
- Illustrer la chaîne de valeur **ingestion → modélisation → documentation**.

### Architecture

```
Météo-France API
    ↓
Ingestion Python
    ↓
DuckDB (raw.*)
    ↓
dbt models
    ↓
Analyses / Visualisations
```
---

## 🛠️ Mise en place

### Installer l'environnement
```bash
make env-setup
```

### Activer l'environnement
```bash
source .venv/bin/activate
```

### Définir les variables d’environnement
Créer un fichier `.env` :
```bash
METEOFRANCE_TOKEN=xxxxxxxxxxxxxxxx
DUCKDB_PATH=data/warehouse.duckdb
```
avec :
- `METEOFRANCE_TOKEN` : la clé API Météo-France  
- `DUCKDB_PATH` : le chemin du fichier DuckDB (par défaut `data/warehouse.duckdb`)

---

## 🔧 Ingestion des données (API → DuckDB)

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

**Paramètres requis :**

* `METEOFRANCE_TOKEN` (clé API)
* `DUCKDB_PATH` (par défaut `data/warehouse.duckdb`)

---

### Mesurer la fraîcheur des sources (dbt)

```bash
make dbt-sources-freshness
```

**Comment ça marche :**

* dbt lit `loaded_at_field: load_time` (défini dans `sources.yml`)
* compare `load_time` à l’horloge actuelle, et applique les seuils :

  * ⚠️ **warn** si `load_time` > **2 h**
  * ⛔ **error** si `load_time` > **4 h**

**Lecture des résultats :**

* ✅ **pass** : la source est à jour
* ⚠️ **warn** : données en retard (surveillance conseillée)
* ⛔ **error** : pipeline considéré **en échec**

**Que faire en cas d’alerte/erreur ?**

1. Relancer l’ingestion :

   ```bash
   make dwh-ingest DEPT=09
   ```
2. Vérifier le token API et la connectivité réseau.

---

### Exécuter les tests de schéma et de données (dbt)

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

## ⚙️ dbt — exécution par actions

### 1) Activer le profil local
```bash
export DBT_PROFILES_DIR=./profiles
```

### 2) Tester la connexion au DWH
```bash
dbt debug
```

### 3) Lancer l’exécution de tous les modèles
```bash
make dbt-build     # deps + run
```

### 4) Exécuter un sous-ensemble de modèles

```bash
dbt run --select stg_obs_hourly      # un modèle
dbt run --select tag:stg     # tous les modèles ayant le tag `stg`
dbt run --full-refresh -s tag:int # full refresh ciblé
```

### 5) Lancer les tests

```bash
make dbt-test    # tous les tests
dbt test -s tag:staging  # cibler un tag
```

### 6) Lancer un rebuild complet

```bash
make dbt-rebuild                     # reset + deps + run --full-refresh + test
```

---

### 📊 Prochaines étapes

* Configurer CI (`dbt build`, tests, docs)
* Publier artefacts (docs/lineage)

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
