# 🧩 Modélisation dbt

Cette section décrit la structure des modèles dbt du projet `weather_dbt`.

---

## Structure

- `staging` : nettoyage, typage, renommage clair
- `intermediate` : calculs intermédiaires, features météo + fenêtres glissantes
- `marts` : tables analytiques et dimensionnelles prêtes BI

Modèles clés :

- `fct_obs_hourly` : fait horaire (tests, contrat de schéma, enrichissements Beaufort/intensités)
- `agg_station_latest_24h` : dernière observation par station avec flags prêts pour le dashboard
- `dim_stations` : dimension géographique
- `dim_beaufort`, `dim_temp_intensity`, `dim_precip_intensity`, `dim_snow_intensity` : dimensions de référence construites depuis les seeds

---

## Modèles incrémentaux

Deux modèles utilisent `materialized: incremental` avec stratégie `merge`
pour éviter un full refresh systématique.
Forcer un rebuild complet :

```bash
make dbt-rebuild
```

---

## Qualité, seeds et docs

- Tests : not_null, unique, relationships, accepted_values + tests custom (`non_negative`, `between_range`, drapeaux vs valeurs).
- Contrats : `fct_obs_hourly` est contracté (types + colonnes fixés, critique pour la BI).
- Seeds : échelle de Beaufort et intensités (température, pluie, neige) alimentent les dimensions BI.
- Exposure : `weather_bi_streamlit` déclare le dashboard Streamlit comme consommateur final.

Docs dbt :

```bash
make dbt-docs-generate   # génère HTML/JSON dans target/
make dbt-docs-serve      # sert la doc sur http://localhost:8080
```

---

## Seeds (référentiels)

Référentiels versionnés dans `weather_dbt/seeds/` :

- `beaufort_scale.csv` : mapping Beaufort (niveau, libellé, plages de vitesse m/s)
- `temp_intensity.csv` : plages de température °C → labels (ex. confort, frais)
- `precip_intensity.csv` : plages de précipitations 24h → labels
- `snow_intensity.csv` : plages de neige 24h → labels

Chargement :

```bash
dbt seed                          # inclus dans make dbt-build
dbt seed --select beaufort_scale  # seed ciblé
```

---

## Macros utiles (sélection)

- Conversions : `kelvin_to_c`, `ms_to_kmh`
- Safe casts : `safe_double`, `safe_int`
- Features météo : `wind_sector`, `visibility_category`, drapeaux gel/pluie/neige
- Time series : `rolling_sum_hours`, `rolling_avg_hours`
- Tests custom : `non_negative`, `between_range`, `*_flag_matches_value`

---

## Exécution dbt

```bash
# Tester la connexion au DWH
dbt debug

# Tous les modèles, tests, snapshots et seeds
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
dbt run -s +exposure:weather_bi_streamlit   # périmètre du dashboard
dbt test -s +exposure:weather_bi_streamlit
```
