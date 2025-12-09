{{ config(materialized='table') }}

select
    simple_level        as beaufort_level,
    simple_label        as beaufort_label,
    ms_min,
    ms_max
from {{ ref('beaufort_scale') }}
