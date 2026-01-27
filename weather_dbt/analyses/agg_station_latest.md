{% docs doc_agg_station_latest %}

# agg_station_latest

Vue "dernier etat" par station : derniere observation horaire disponible issue de
`fct_obs_hourly`, enrichie de metriques sur fenetres glissantes 24h (precipitations,
neige, temperature) et des labels BI (intensites, Beaufort) et des coordonnees.

**Grain** : 1 ligne = 1 station_id (derniere validity_time_utc disponible)
**Usage** : source directe du dashboard Streamlit (exposure `weather_bi_streamlit`).

Les colonnes `is_*` sont des drapeaux booleens pre-calcules a partir des champs
d'intensite 24h et de Beaufort, pour simplifier les filtres et cartes dans la BI.

{% enddocs %}
