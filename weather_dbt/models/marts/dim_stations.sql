-- models/marts/dim_stations.sql
{{ config(materialized='table') }}

select
    station_id,
    station_name,
    latitude,
    longitude,
    altitude
from {{ ref('stg_stations') }}
