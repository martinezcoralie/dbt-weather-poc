{% macro to_date(ts_expr) -%}
  {{ adapter.dispatch('to_date', 'weather_dbt')(ts_expr) }}
{%- endmacro %}

{% macro duckdb__to_date(ts_expr) -%}
  cast({{ ts_expr }} as date)
{%- endmacro %}

{% macro bigquery__to_date(ts_expr) -%}
  date({{ ts_expr }})
{%- endmacro %}
