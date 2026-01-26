-- macros/safe_casts.sql
{% macro safe_double(col) -%}
  {{ adapter.dispatch('safe_double', 'weather_dbt')(col) }}
{%- endmacro %}

{% macro duckdb__safe_double(col) -%}
  try_cast(nullif(cast({{ col }} as varchar), '') as double)
{%- endmacro %}

{% macro bigquery__safe_double(col) -%}
  safe_cast(nullif(cast({{ col }} as string), '') as float64)
{%- endmacro %}


{% macro safe_int(col) -%}
  {{ adapter.dispatch('safe_int', 'weather_dbt')(col) }}
{%- endmacro %}

{% macro duckdb__safe_int(col) -%}
  try_cast(nullif(cast({{ col }} as varchar), '') as integer)
{%- endmacro %}

{% macro bigquery__safe_int(col) -%}
  safe_cast(nullif(cast({{ col }} as string), '') as int64)
{%- endmacro %}
