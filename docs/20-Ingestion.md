# Ingestion (API → DuckDB `raw`)

L’ingestion alimente le schéma **`raw`** du warehouse DuckDB. On conserve volontairement la structure “brute” : les transformations sémantiques et la normalisation d’unités sont faites en **staging dbt**.

## Pré-requis
`METEOFRANCE_TOKEN` disponible (via `.env`). Voir : [10-Setup.md](10-Setup.md)

## Ce que fait l’ingestion

- Récupère les stations et les observations horaires (fenêtre des **dernières 24 h**).
- Écrit en brut dans DuckDB :
  - `raw.stations`
  - `raw.obs_hourly`
- Ajoute deux champs techniques :
  - `load_time` (UTC)
  - `dept_code`

## Qualité & idempotence (niveau raw)

- Noms de colonnes identiques à la source
- Types inchangés
- Déduplication par clé logique :

```text
(validity_time, geo_id_insee, reference_time)
```

## Exécuter l’ingestion (local)

```bash
make dwh-ingest DEPT=75
```
Codes département attendus : format sans zéro initial (`9`, `75` ; pas `09`).

## Exécuter l’ingestion (Docker Compose)


```bash
DEPT=75 docker compose --profile ingest run --rm ingest
```

## Diagnostic rapide

```bash
make dwh-tables
make dwh-table TABLE=raw.obs_hourly
```

Prochaine étape : [30-dbt-Modeling.md](30-dbt-Modeling.md).
