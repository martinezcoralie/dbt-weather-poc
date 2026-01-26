{% docs doc_agg_station_latest_24h %}

# agg_station_latest_24h

Vue "dernieres 24h" par station, issue de `fct_obs_hourly` et enrichie des labels
BI (intensites precipitations, neige, temperature, Beaufort) et des coordonnees.

**Grain** : 1 ligne = 1 station_id (derniere validity_time_utc disponible)
**Usage** : source directe du dashboard Streamlit (exposure `weather_bi_streamlit`).

Les colonnes `is_*` sont des drapeaux booleens pre-calcules pour simplifier les
filtres et cartes dans la BI.

{% enddocs %}
