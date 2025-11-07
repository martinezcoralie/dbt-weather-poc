-- models/intermediate/int_obs_windowing.sql
{{ config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns'
) }}

with src as (
  select *
  from {{ ref('int_obs_features') }}
  {% if is_incremental() %}
    -- Recalcule un buffer de 24h
    where validity_time_utc >= (
      select coalesce(
        date_add(max(validity_time_utc), INTERVAL '-25 hours'),
        TIMESTAMP '1900-01-01'
      )
      from {{ this }}
    )
  {% endif %}
)

select
  event_id,
  station_id,
  validity_time_utc,

  -- Précip cumuls
  {{ rolling_sum_hours('precip_mm_h', 'validity_time_utc', 'station_id', 1) }}  as precip_1h_mm,
  {{ rolling_sum_hours('precip_mm_h', 'validity_time_utc', 'station_id', 3) }}  as precip_3h_mm,
  {{ rolling_sum_hours('precip_mm_h', 'validity_time_utc', 'station_id', 24) }} as precip_24h_mm,

  -- Snow cumuls
  {{ rolling_sum_hours('snow_depth_m', 'validity_time_utc', 'station_id', 1) }}  as snow_1h_m,
  {{ rolling_sum_hours('snow_depth_m', 'validity_time_utc', 'station_id', 3) }}  as snow_3h_m,
  {{ rolling_sum_hours('snow_depth_m', 'validity_time_utc', 'station_id', 24) }} as snow_24h_m,

  -- Temp cumuls
  {{ rolling_avg_hours('temperature_c', 'validity_time_utc', 'station_id', 1) }}  as temp_1h_c,
  {{ rolling_avg_hours('temperature_c', 'validity_time_utc', 'station_id', 3) }}  as temp_3h_c,
  {{ rolling_avg_hours('temperature_c', 'validity_time_utc', 'station_id', 24) }} as temp_24h_c

from src
