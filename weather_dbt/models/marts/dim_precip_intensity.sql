{{ config(materialized='table') }}

select
    cast(row_number() over (order by coalesce(max_mm, 9999), min_mm) as integer) as intensity_level,
    min_mm,
    max_mm,
    label
from {{ ref('precip_intensity') }}
