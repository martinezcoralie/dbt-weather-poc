# 📥 Ingestion des données (API → DuckDB)

Cette étape constitue le point d’entrée du pipeline et alimente le schéma `raw` du warehouse DuckDB, sur lequel se base dbt pour la modélisation.

L’ingestion est assurée par les scripts Python du dossier `scripts/ingestion/`, notamment :
- `fetch_meteofrance_paquetobs.py` pour la récupération depuis l’API Météo-France,
- `write_duckdb_raw.py` pour l’écriture des données brutes dans DuckDB.

---

## Lancer une ingestion départementale

```bash
make dwh-ingest DEPT=75
```

**Ce que fait la commande :**

* crée `warehouse.duckdb` si absent ;
* interroge l’API Météo-France (dernières **24 h**) pour le département `DEPT` ;
* écrit en **brut** dans `raw.stations` et `raw.obs_hourly`.

---

## Garantie du niveau *raw*

* Noms de colonnes strictement identiques à la source  
* Types inchangés  
* Aucune normalisation d’unités / sémantique (fait plus tard en staging dbt)  
* Champs ajoutés : `load_time` (UTC) et `dept_code`

---

## Idempotence & déduplication

Les doublons sont empêchés via la clé logique :

```text
(validity_time, geo_id_insee, reference_time)
```

En cas de retard de fraîcheur, relancer l’ingestion :

```bash
make dwh-ingest DEPT=9
```