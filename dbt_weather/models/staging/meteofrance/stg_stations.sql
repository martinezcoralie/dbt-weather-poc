-- models/staging/meteofrance/stg_stations.sql
{{ config(materialized='view') }}

select 
    id_station as station_id,
    nom_usuel as station_name,
    cast(latitude as double) as latitude,
    cast(longitude as double) as longitude,
    cast(altitude as double) as altitude,
    try_cast(date_ouverture as date) as opening_date,
from {{ source('raw', 'stations')}}