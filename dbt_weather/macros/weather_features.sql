-- macros/weather_features.sql
{# Secteur de vent sur 8 points cardinaux #}
{% macro wind_sector(dir_deg) -%}
  case
    when {{ dir_deg }} is null then null
    when {{ dir_deg }} >= 337.5 or {{ dir_deg }} < 22.5  then 'N'
    when {{ dir_deg }} < 67.5  then 'NE'
    when {{ dir_deg }} < 112.5 then 'E'
    when {{ dir_deg }} < 157.5 then 'SE'
    when {{ dir_deg }} < 202.5 then 'S'
    when {{ dir_deg }} < 247.5 then 'SW'
    when {{ dir_deg }} < 292.5 then 'W'
    else 'NW'
  end
{%- endmacro %}

{# Beaufort (m/s -> échelle 0–12) #}
{% macro beaufort(speed_ms) -%}
  case
    when {{ speed_ms }} is null then null
    when {{ speed_ms }} < 0.5 then 0
    when {{ speed_ms }} < 1.6 then 1
    when {{ speed_ms }} < 3.4 then 2
    when {{ speed_ms }} < 5.5 then 3
    when {{ speed_ms }} < 8.0 then 4
    when {{ speed_ms }} < 10.8 then 5
    when {{ speed_ms }} < 13.9 then 6
    when {{ speed_ms }} < 17.2 then 7
    when {{ speed_ms }} < 20.8 then 8
    when {{ speed_ms }} < 24.5 then 9
    when {{ speed_ms }} < 28.5 then 10
    when {{ speed_ms }} < 32.7 then 11
    else 12
  end
{%- endmacro %}

{# Visibilité -> catégories #}
{% macro visibility_category(visibility_m) -%}
  case
    when {{ visibility_m }} is null then null
    when {{ visibility_m }} < 200 then 'dense_fog'
    when {{ visibility_m }} < 1000 then 'fog'
    when {{ visibility_m }} < 5000 then 'haze'
    else 'good'
  end
{%- endmacro %}

{# Drapeaux simples #}
{% macro freezing_flag(temp_c) -%} case when {{ temp_c }} <= 0 then 1 end {%- endmacro %}
{% macro precip_flag(precip_mm) -%} case when {{ precip_mm }} > 0 then 1 end {%- endmacro %}
{% macro snow_on_ground_flag(snow_depth_m) -%}
  case when {{ snow_depth_m }} is not null and {{ snow_depth_m }} > 0 then 1 end
{%- endmacro %}