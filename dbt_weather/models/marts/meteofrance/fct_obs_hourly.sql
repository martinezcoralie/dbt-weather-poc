{{ config(
  materialized='incremental',
  unique_key='event_id',
  on_schema_change='sync_all_columns'
) }}
select
  event_id,
  station_id,
  validity_time_utc,
  temperature_c,
  humidity_pct,
  precip_mm,
  wind_speed_ms,
  pressure_sea_pa
from {{ ref('int_obs_enriched') }}
{% if is_incremental() %}
where validity_time_utc > (select coalesce(max(validity_time_utc), '1900-01-01') from {{ this }})
{% endif %}
