-- models/staging/meteofrance/stg_stations.sql
{{ config(materialized='view') }}

with base as (
  select
    -- Identifiant / nom (nettoyage léger)
    nullif(trim(Id_station), '')                         as station_id,
    lower(nullif(trim(Nom_usuel), ''))                   as station_name,

    -- Coordonnées : numeric + bornes géographiques
    case
      when {{ safe_double('Latitude') }} between -90 and 90
      then {{ safe_double('Latitude') }}
    end                                                  as latitude,

    case
      when {{ safe_double('Longitude') }} between -180 and 180
      then {{ safe_double('Longitude') }}
    end                                                  as longitude,

    -- Altitude en mètres (bornes larges : -500m..9000m pour couvrir cas extrêmes)
    case
      when {{ safe_double('Altitude') }} between -500 and 9000
      then {{ safe_double('Altitude') }}
    end                                                  as altitude,

    -- Date d'ouverture (date civile, pas de TZ)
    try_cast(nullif(trim(Date_ouverture), '') as date)   as opening_date

  from {{ source('raw', 'stations') }}
)

select * from base