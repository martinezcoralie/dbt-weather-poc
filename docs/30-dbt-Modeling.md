# dbt — Modélisation, qualité et performance

Cette page décrit la structure dbt du projet `weather_dbt`, et les éléments visibles dans le code et dans dbt Docs (tests, contrats, macros, lineage, exposure).

## Layering

- `staging` : nettoyage, typage, renommage clair
- `intermediate` : calculs intermédiaires (features météo + fenêtres glissantes)
- `marts` : modèles analytiques prêts BI

```text
raw.* → staging → intermediate → marts → exposure Streamlit
```

## Modèles clés

- `fct_obs_hourly` : fait horaire (tests, contrat de schéma, enrichissements Beaufort / intensités)
- `agg_station_latest_24h` : dernière observation par station, avec flags prêts dashboard
- `dim_stations` : dimension géographique
- Dimensions de référence construites depuis des seeds :
  - `dim_beaufort`
  - `dim_temp_intensity`
  - `dim_precip_intensity`
  - `dim_snow_intensity`

## Incrémental (stratégie `merge`)

Certains modèles sont matérialisés en `incremental` avec stratégie `merge` pour éviter un full refresh systématique.

Rebuild complet (reset + `--full-refresh`) :

```bash
make dbt-rebuild
```

## Qualité, contrats, exposure

- Tests : `not_null`, `unique`, `relationships`, `accepted_values` + tests custom (ex. `non_negative`, `between_range`, cohérence drapeaux ↔ valeurs).
- Contrats : `fct_obs_hourly` et `agg_station_latest_24h` sont contractés (types + colonnes stabilisés, utile pour sécuriser la consommation BI).
- Exposure : `weather_bi_streamlit` déclare le dashboard Streamlit comme consommateur final.

## Sources & Freshness

Les sources dbt sont déclarées avec un champ de fraîcheur (`loaded_at_field`) afin de :
- mesurer la fraîcheur des données ingérées,
- déclencher des alertes / checks avant calcul des marts,
- rendre le pipeline plus orienté production.

Commandes utiles :

```bash
make dbt-sources-test        # tests sur les sources
make dbt-sources-freshness   # fraîcheur des sources
make dbt-sources-check       # combo tests + fraîcheur
```

## Seeds

Référentiels versionnés dans `weather_dbt/seeds/` :

- `beaufort_scale.csv`
- `temp_intensity.csv`
- `precip_intensity.csv`
- `snow_intensity.csv`

Chargement :

```bash
dbt seed                          # inclus dans make dbt-build
dbt seed --select beaufort_scale  # seed ciblé
```

## Macros utiles

- Conversions : `kelvin_to_c`, `ms_to_kmh`
- Safe casts : `safe_double`, `safe_int`
- Features météo : `wind_sector`, `visibility_category`, drapeaux gel/pluie/neige
- Time series : `rolling_sum_hours`, `rolling_avg_hours`
- Tests custom : `non_negative`, `between_range`, `*_flag_matches_value`

## Commandes dbt (local)

```bash
dbt debug
make dbt-build
make dbt-test
```

Sélections utiles :

```bash
dbt run --select stg_obs_hourly
dbt run --select tag:stg
dbt run --full-refresh -s tag:mart
dbt run -s +exposure:weather_bi_streamlit
dbt test -s +exposure:weather_bi_streamlit
```


## Pourquoi cela compte (client / recruteur)

* **Tests + contrats** : sécurise la consommation BI, réduit les régressions et les surprises en prod.
* **Incrémental** : évite les recalculs complets, accélère les itérations et maîtrise les coûts de run.
* **Seeds + macros** : encode le métier et normalise les transformations (cohérence, réutilisabilité).
* **Exposure** : rend explicite la consommation (dashboard) et permet des exécutions ciblées.


Prochaine étape : [31-dbt-Docs-Lineage.md](31-dbt-Docs-Lineage.md).


