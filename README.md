# dbt-weather-poc

Pipeline d’ingestion et de modélisation Météo-France (Paquet Observations DPPaquetObs)  
Basé sur **DuckDB**, **Python**, et **dbt**.

> Ce projet DBT collecte et historise les observations météo horaires de Météo France pour le département de l’Ariège afin d’analyser la qualité de vie climatique selon les zones (soleil, humidité, vent, pluie).

## 💡 Objectifs

- Démontrer un flux de données complet **API → Warehouse → dbt**, portable et reproductible.
- Illustrer la chaîne de valeur **ingestion → modélisation → documentation**.

## 🧩 Architecture

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

## 🛠️ Installation (dev local)

```bash
make install
```
---

## 🔐 Variables d’environnement

Créer un fichier `.env` :

```bash
METEOFRANCE_TOKEN=xxxxxxxxxxxxxxxx
DUCKDB_PATH=./warehouse.duckdb     # optionnel
```

- `METEOFRANCE_TOKEN` : clé API Météo-France  
- `DUCKDB_PATH` : chemin du fichier DuckDB (par défaut `./warehouse.duckdb`)

---

## 🔧 Ingestion des données (API → DuckDB)

### Lancer une ingestion départementale

```bash
make write DEPT=75
```
* Crée `warehouse.duckdb`
* Charge les données brutes dans `raw.stations` et `raw.obs_hourly`

### Faire une inspection rapide

```bash
make peek
```
Permet de visualiser un extrait des données directement dans le terminal.

### Contrat RAW

La couche `raw.*` correspond **strictement** au schéma renvoyé par l’API :

✅ Noms de colonnes inchangés  
✅ Types conservés (strings)  
✅ Structure fidèle au CSV API  
✅ Métadonnée ajoutée : `load_ts` (UTC), `dept_code`
✅ Déduplication via clé logique (`station_code_insee`, `validity_time` pour horaire)

❌ aucun cast  
❌ aucun renommage  
❌ aucune normalisation d’unité  
❌ aucun strip/lower

Toutes les transformations se font dans **dbt (staging)**.


### 🧰 Scripts ingestion

#### `scripts/ingestion/fetch_meteofrance_paquetobs.py`

Client fetch-only :

- Appels API `/liste-stations` et `/paquet/horaire`
- Parsing CSV **sans aucune transformation**
- Retourne des DataFrames RAW

#### `scripts/ingestion/write_duckdb_raw.py`

Writer vers DuckDB :

- création du schéma `raw`
- `load_ts` et `dept_code` ajoutés
- déduplication sur PK logique

---
## 🔢 Explorer le warehouse avec DuckDB CLI

### Installation du client DuckDB

**macOS**
```bash
brew install duckdb
```

### Ouvrir le shell interactif
```bash
duckdb warehouse.duckdb
```

### Commandes utiles
```sql
show;                                  -- liste les tables
select count(*) from raw.stations;     -- compte les lignes d'une table
select * from raw.obs_hourly limit 5;  -- aperçu des données
show raw.stations;                     -- affiche le schéma d'une table
```

---

## ⚙️ Configuration du profil dbt

Ce projet utilise un **profil dbt local** pour rester totalement autonome et reproductible, sans dépendance au dossier `~/.dbt`.

Le fichier de profil est stocké dans :
```
profiles/profiles.yml
```

### 📦 Utilisation

Avant d'exécuter dbt, indiquez à dbt où trouver le profil :

```bash
export DBT_PROFILES_DIR=./profiles
```

Puis lancez vos commandes :

```bash
dbt debug
dbt run
dbt test
```

---

### 📊 Prochaines étapes

* Configurer CI (`dbt build`, tests, docs)
* Publier artefacts (docs/lineage)

---

**Auteur :** Coralie
