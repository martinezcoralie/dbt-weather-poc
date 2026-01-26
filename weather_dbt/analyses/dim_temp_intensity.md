{% docs doc_dim_temp_intensity %}

# dim_temp_intensity

Dimension d'interpretation BI de la temperature moyenne glissante sur 24h (C),
derivee du seed `temp_intensity`. Jointee sur `fct_obs_hourly.temp_24h_c` pour
produire les champs d'intensite 24h.

**Grain** : 1 ligne = 1 niveau d'intensite
**Usage** : classer la temperature 24h en categories metier.

{% enddocs %}
