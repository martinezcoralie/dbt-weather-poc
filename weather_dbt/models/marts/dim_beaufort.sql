{{ config(materialized='table') }}

select
  level        as beaufort_level,
  label        as beaufort_label,
  ms_min,
  ms_max
from {{ ref('beaufort_scale') }}
