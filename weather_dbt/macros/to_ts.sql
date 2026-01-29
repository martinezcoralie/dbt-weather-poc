{% macro to_ts(col) -%}
  {{ adapter.dispatch('to_ts', 'weather_dbt')(col) }}
{%- endmacro %}

{% macro duckdb__to_ts(col) -%}
  try_cast({{ col }} as timestamptz)
{%- endmacro %}

{% macro bigquery__to_ts(col) -%}
  safe_cast({{ col }} as timestamp)
{%- endmacro %}
