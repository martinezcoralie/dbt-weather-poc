# dbt-weather-poc

**PoC Météo :** ingestion des données Météo-France (API Paquet Observations) vers DuckDB (`raw.*`).

> Ce projet DBT collecte et historise les observations météo horaires de Météo France pour le département de l’Ariège afin d’analyser la qualité de vie climatique selon les zones (soleil, humidité, vent, pluie).
> En parallèle, une lecture humoristique des mêmes indicateurs traduit la météo en unités du quotidien — une façon ludique de montrer comment transformer la donnée en récit.


### 💡 Objectif

Démontrer un flux de données complet **API → Warehouse → dbt**, portable et reproductible.

Illustrer la chaîne de valeur **ingestion → modélisation → documentation**.

### 🧩 Architecture

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

## 🔧 Ingestion des données (API → DuckDB)

```bash
make write DEPT=75
```

* Crée `warehouse.duckdb`
* Charge les données brutes dans `raw.stations` et `raw.obs_hourly`
---
### 🔍 Inspection rapide

```bash
make peek
```
Permet de visualiser un extrait des données directement dans le terminal.

---

## 🗑️ Nettoyer

```bash
make clean-db
```
Supprime la base DuckDB locale.

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

* Ajouter `dbt_project.yml` + modèles `stg_*/int_*/mart_*`
* Configurer CI (`dbt build`, tests, docs)
* Publier artefacts (docs/lineage)

---

**Auteur :** Coralie
