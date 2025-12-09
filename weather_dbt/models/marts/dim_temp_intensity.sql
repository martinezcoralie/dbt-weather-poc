{{ config(materialized='table') }}

select
    cast(row_number() over (order by coalesce(max_c, 9999), min_c) as integer) as intensity_level,
    min_c,
    max_c,
    label as intensity_label
from {{ ref('temp_intensity') }}
