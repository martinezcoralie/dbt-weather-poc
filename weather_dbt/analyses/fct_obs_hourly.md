{% docs fct_obs_hourly_doc %}

# fct_obs_hourly

Hourly fact table built from:
- derived metrics (rolling windows) from `int_obs_windows`,
- enriched features (units, wind sectors, flags, conversions) from `int_obs_features`,
- simplified Beaufort attributes via `dim_beaufort`,
- precipitation, snow, and temperature intensity dimensions via
  `dim_precip_intensity`, `dim_snow_intensity`, and `dim_temp_intensity`.

**Grain**: 1 row = 1 station_id × 1 validity_time_utc  
**Use**: factual base for data quality checks and aggregations. Feeds
`agg_station_latest`, used by the Streamlit dashboard.
**Partition**: `validity_date` (BigQuery optimization).
**Materialization**: incremental (merge) with a buffer on `validity_date`.

Tests with `severity: warn` target fields coming directly from raw Météo-France
measurements, which can contain operational noise. Logical inconsistencies
(e.g., flags) are tested strictly.

{% enddocs %}
