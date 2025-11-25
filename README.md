# dbt-weather-poc

Pipeline d’ingestion et de modélisation Météo-France (Paquet Observations DPPaquetObs)  
Basé sur **DuckDB**, **Python**, et **dbt**.

> Ce projet DBT collecte et historise les observations météo horaires de Météo France pour le département de l’Ariège afin d’analyser la qualité de vie climatique selon les zones (soleil, humidité, vent, pluie).

Les marts sont exposés dans un petit dashboard Streamlit (cf. section 📊 Visualisation BI).

## 💡 Objectifs

- Démontrer un flux de données complet **API → Warehouse → dbt**, portable et reproductible.
- Illustrer la chaîne de valeur **ingestion → modélisation → documentation**.
- Montrer l’usage de modèles **incrémentaux dbt** pour optimiser les mises à jour de données horaires.

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


### Activer le profil local
```bash
export DBT_PROFILES_DIR=./profiles
```

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
dbt test -s tag:staging  # cibler un tag
```

### 4) Lancer un rebuild complet

```bash
make dbt-rebuild    # reset + deps + run --full-refresh + test
```

### À propos des modèles incrémentaux

Ce projet utilise des modèles **incrémentaux dbt** pour éviter de recalculer l’historique complet à chaque exécution.

Concrètement :

* seules les nouvelles observations météo sont traitées ;
* l’historique déjà calculé est conservé ;
* l’exécution est plus rapide et plus économique qu’un *full refresh*.

Les modèles concernés :

* `intermediate.int_obs_features`
* `intermediate.int_obs_windowing`

Ces modèles sont basés sur la clé `event_id` et utilisent la stratégie `merge`.

Pour forcer un recalcul complet :

```bash
make dbt-rebuild
```

---

## 📚 Documentation dbt (catalogue + lineage)

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

## 📊 Visualisation BI (dashboard Streamlit)

Une fois les données ingérées et les modèles dbt exécutés, on peut explorer les marts via une petite app Streamlit.

### Lancer le dashboard

```bash
# 1) S'assurer que l'environnement est prêt
make env-setup
source .venv/bin/activate

# 2) Lancer l'application Streamlit
streamlit run apps/bi-streamlit/app.py
```

Par défaut, le dashboard est disponible sur :

* [http://localhost:8501](http://localhost:8501)

Le dashboard lit directement dans le fichier DuckDB (`DUCKDB_PATH`, par défaut `data/warehouse.duckdb`)
et s’appuie sur les modèles marts, notamment :

* `marts.meteofrance.fct_obs_hourly`
* `marts.meteofrance.dim_stations`
* `marts.meteofrance.agg_daily_station`

### Models en amont du dashboard (exposure dbt)

Ce projet définit un **exposure dbt** nommé `weather_bi_streamlit`, qui représente le dashboard Streamlit comme un consommateur final des données.

Cet exposure permet d’**identifier explicitement** quels modèles dbt alimentent le dashboard, et donc de **sélectionner, tester ou exécuter uniquement le périmètre réellement utilisé** par la BI.

```bash
# Voir les modèles qui alimentent le dashboard
dbt ls -s +exposure:weather_bi_streamlit

# Exécuter uniquement ces modèles
dbt run -s +exposure:weather_bi_streamlit
dbt test -s +exposure:weather_bi_streamlit
```

💡 **Intérêt**
Si, plus tard, le projet comporte d’autres modèles non utilisés par le dashboard
(ex. nouveaux marts, analyses, features), ces commandes permettent de :

* ne construire **que** ce qui alimente le dashboard ;
* réduire le temps d’exécution ;
* éviter de tester ou builder des modèles hors scope BI.

---

### 📊 Prochaines étapes

* Configurer CI (`dbt build`, tests, docs)
* Publier artefacts (docs/lineage)
* Enrichir l’exposition `weather_bi_streamlit` au fil des évolutions du projet

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
