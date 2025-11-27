-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
  {# Si un +schema est défini, utilise-le tel quel (staging/intermediate/marts) #}
  {%- if custom_schema_name is not none and custom_schema_name|length > 0 -%}
    {{ custom_schema_name | trim }}
  {%- else -%}
    {{ target.schema }}
  {%- endif -%}
{%- endmacro %}
