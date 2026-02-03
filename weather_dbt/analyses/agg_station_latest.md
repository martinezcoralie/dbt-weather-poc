{% docs doc_agg_station_latest %}

# agg_station_latest

"Latest state" view per station: the most recent hourly observation from
`fct_obs_hourly`, enriched with 24h rolling metrics (precipitation, snow,
temperature), BI labels (intensity, Beaufort), and coordinates.

**Grain**: 1 row = 1 station_id (latest available validity_time_utc)
**Use**: direct source for the Streamlit dashboard (exposure `weather_bi_streamlit`).
**Materialization**: incremental (merge) filtered on `fct_obs_hourly.validity_date`.

`is_*` columns are precomputed boolean flags derived from 24h intensity fields
and Beaufort, to simplify BI filters and maps.

{% enddocs %}
