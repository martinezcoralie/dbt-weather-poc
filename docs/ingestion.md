# 📥 Ingestion des données (API → DuckDB)

Cette étape constitue le point d’entrée du pipeline et alimente le schéma `raw` du warehouse DuckDB, sur lequel se base dbt pour la modélisation.

L’ingestion est assurée par les scripts Python du dossier `scripts/ingestion/` :
- `fetch_meteofrance_paquetobs.py` pour la récupération depuis l’API Météo-France,
- `write_duckdb_raw.py` pour l’écriture des données brutes dans DuckDB.

---

## Prérequis

- Avoir créé l’environnement Python : `make env-setup && source .venv/bin/activate`
- Variables d’environnement (via `.env`) :
  - `METEOFRANCE_TOKEN` : clé API Météo-France valide (Voir [🔑 Obtenir une clé API Météo-France](meteofrance_token.md))
  - `DUCKDB_PATH` : chemin du fichier DuckDB (ex. `data/warehouse.duckdb`)
- Profil dbt pointant vers le warehouse : `export DBT_PROFILES_DIR=./profiles`

---

## Lancer une ingestion départementale

```bash
make dwh-ingest DEPT=75
```

**Ce que fait la commande :**

- crée `warehouse.duckdb` si absent ;
- interroge l’API Météo-France (dernières **24 h**) pour le département `DEPT` ;
- écrit en **brut** dans `raw.stations` et `raw.obs_hourly` ;

---

## Qualité & idempotence (niveau raw)

* Noms de colonnes strictement identiques à la source  
* Types inchangés  
* Aucune normalisation d’unités / sémantique (fait plus tard en staging dbt)  
* Champs ajoutés : `load_time` (UTC) et `dept_code`

Déduplication via la clé logique :
```text
(validity_time, geo_id_insee, reference_time)
```
`raw.stations` : clé `Id_station`.

---

## Période et retries

- Période : dernières 24 h.
- En cas de retard de fraîcheur, relancer l’ingestion (la déduplication protège).
- Erreurs courantes : token absent/expiré, quota, réseau → vérifier `.env` et relancer.

---

## Entrées / sorties

- Entrée : API DPPaquetObs (CSV) — endpoints `/liste-stations` et `/paquet/horaire`
- Sorties : tables DuckDB `raw.stations` et `raw.obs_hourly` (mêmes noms de colonnes que la source)
---

## Diagnostic rapide après ingestion

- Vérifier les tables présentes : `make dwh-tables`
- Compter/inspecter `raw.obs_hourly` : `make dwh-table TABLE=raw.obs_hourly`
