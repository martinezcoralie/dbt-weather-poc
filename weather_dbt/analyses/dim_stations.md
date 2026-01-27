{% docs doc_dim_stations %}

# Dimension `dim_stations`

Cette dimension fournit une vue simplifiée et stable des stations météo :

- identifiant technique de la station (`station_id`) ;
- nom lisible (`station_name`) pour les usages BI ;
- coordonnées géographiques (`latitude`, `longitude`) ;
- altitude.

## Rôle dans le modèle de données

`dim_stations` sert principalement à :

- afficher des libellés compréhensibles dans le dashboard (plutôt qu’un code brut) ;
- positionner les stations sur une carte à partir des coordonnées ;

Dans ce projet, la dimension est consommée par `agg_station_latest` pour
exposer nom et coordonnées dans le dashboard.

Les contrôles de qualité (plages de latitude/longitude/altitude, unicité de la station, etc.)
sont appliqués en amont dans le modèle de staging `stg_stations`. La dimension projette ensuite
les colonnes nécessaires pour la consommation analytique.

## Fréquence de changement

Le référentiel de stations Météo-France évolue peu dans le temps : il s’agit d’une dimension
à faible fréquence de changement, utilisée comme table de référence.

{% enddocs %}
