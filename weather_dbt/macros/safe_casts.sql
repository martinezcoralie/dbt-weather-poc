-- macros/safe_casts.sql
{% macro safe_double(col) %} try_cast(nullif({{ col }}, '') as double) {% endmacro %}
{% macro safe_int(col) %}    try_cast(nullif({{ col }}, '') as integer) {% endmacro %}