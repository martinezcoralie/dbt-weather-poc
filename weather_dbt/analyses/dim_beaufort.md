{% docs doc_dim_beaufort %}

# dim_beaufort

Dimension simplifiee de l'echelle de Beaufort (5 niveaux agreges) avec libelles
metiers et bornes min/max de vitesse du vent en m/s. Utilisee pour enrichir
`fct_obs_hourly` via une jointure sur la vitesse.

**Grain** : 1 ligne = 1 niveau Beaufort simplifie (1 a 5)
**Usage** : fournir un niveau Beaufort lisible pour les marts et le dashboard
via `fct_obs_hourly`.

{% enddocs %}
