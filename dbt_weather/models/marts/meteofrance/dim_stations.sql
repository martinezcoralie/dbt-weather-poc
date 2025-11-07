-- models/marts/dim_stations.sql
{{ config(materialized='table') }}

select
  station_id,
  station_name
from {{ ref('stg_stations') }}
