{% docs fct_obs_hourly_doc %}

# fct_obs_hourly

Table de faits horaire issue de l’assemblage :
- des métriques dérivées (fenêtres glissantes) depuis `int_obs_windows`,
- des features enrichies (unités, secteurs de vent, flags, conversions) depuis `int_obs_features`,
- des attributs de référence station et Beaufort simplifié via `dim_stations` et `dim_beaufort`,
- des dimensions d’intensité précipitations, neige et température via `dim_precip_intensity`,
  `dim_snow_intensity` et `dim_temp_intensity`.

**Grain** : 1 ligne = 1 station_id × 1 validity_time_utc  
**Usage** : base factuelle pour contrôles qualité et agrégations. Alimente `agg_station_latest_24h`
utilisé par le dashboard Streamlit.

Les tests en `severity: warn` concernent les champs issus directement des mesures brutes Météo-France, susceptibles de contenir du bruit opérationnel. Les incohérences logiques (ex. flags) sont, elles, testées de manière stricte.

{% enddocs %}
