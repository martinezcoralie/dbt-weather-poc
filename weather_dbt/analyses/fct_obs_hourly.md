{% docs fct_obs_hourly_doc %}

# fct_obs_hourly

Table de faits horaire des observations météo rassemblant :
- les fenêtres glissantes (int_obs_windowing)
- les features météo atomiques (int_obs_features)
- les attributs station (dim_stations).

Modèle final destiné au BI.

Grain : 1 ligne par (station_id, validity_time_utc)

Principales métriques :
- precip_1h_mm, precip_3h_mm, precip_24h_mm
- temp_1h_c, temp_3h_c, temp_24h_c
- flags météo (freezing_flag, precip_flag, etc.)

Use cases :
- Suivi de la météo par station
- Construction de KPIs journaliers / hebdomadaires
- Base pour la détection de dérive climatique locale

{% enddocs %}
