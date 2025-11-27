# 📥 Ingestion des données (API → DuckDB)

Cette étape interroge l’API Météo-France et stocke les données brutes dans DuckDB (`raw.*`).

## Lancer une ingestion départementale

```bash
make dwh-ingest DEPT=75
```

**Ce que fait la commande :**

* crée `warehouse.duckdb` si absent ;
* interroge l’API Météo-France (dernières **24 h**) pour le département `DEPT` ;
* écrit en **brut** dans `raw.stations` et `raw.obs_hourly`.

**Garantie de “raw” :**

* Noms de colonnes strictement identiques à la source  
* Types inchangés  
* Aucune normalisation d’unités / sémantique (fait plus tard en staging dbt)  
* Champs ajoutés : `load_time` (UTC) et `dept_code`

**Idempotence & déduplication :**

Les doublons sont empêchés via la clé logique :

```text
(validity_time, geo_id_insee, reference_time)
```

En cas de retard de fraîcheur, relancer l’ingestion :

```bash
make dwh-ingest DEPT=9
```