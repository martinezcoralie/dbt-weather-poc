{% docs fct_obs_hourly_doc %}

# fct_obs_hourly

Table de faits horaire issue de l’assemblage :
- des métriques dérivées (fenêtres glissantes) depuis `int_obs_windows`,
- des features enrichies (unités, secteurs de vent, flags, conversions) depuis `int_obs_features`,
- des attributs de référence station et Beaufort via `dim_stations` et `dim_beaufort`.

**Grain** : 1 ligne = 1 station_id × 1 validity_time_utc  
**Usage** : base analytique pour suivi météo et visualisation BI.

Les tests en `severity: warn` concernent les champs issus directement des mesures brutes Météo-France, susceptibles de contenir du bruit opérationnel. Les incohérences logiques (ex. flags) sont, elles, testées de manière stricte.

{% enddocs %}

