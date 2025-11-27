# 🧩 Modélisation dbt

## Structure

* `staging` : nettoyage, typage, renommage clair
* `intermediate` : calculs intermédiaires, features météo
* `marts` : tables analytiques et dimensionnelles

Modèles clés :

* `fct_obs_hourly` (table de faits horaire)
* `dim_stations` (dimension géographique des stations)

## Modèles incrémentaux

Deux modèles utilisent `materialized: incremental` avec stratégie `merge`
pour éviter un full refresh systématique.

Forcer un rebuild complet :

```bash
make dbt-rebuild
```

## Exécution dbt

```bash
# Tester la connexion au DWH
dbt debug

# Tous les modèles
make dbt-build

# Tous les tests
make dbt-test
```

Exemples de sélections ciblées :

```bash
dbt run --select stg_obs_hourly        # un modèle
dbt run --select tag:stg               # tous les modèles taggés stg
dbt run --full-refresh -s tag:mart     # full refresh ciblé sur les marts
dbt test -s tag:mart                   # tests sur les marts
```