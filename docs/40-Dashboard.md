# Dashboard Streamlit (consommation + exposure dbt)

Une fois les données ingérées et les modèles dbt exécutés, on peut explorer les marts via l’application Streamlit.

## Prérequis

- Warehouse alimenté (`make dwh-ingest`) puis modèles dbt calculés (`make dbt-build`)
- Chemin DuckDB configuré (par défaut `data/warehouse.duckdb`)

## Lancer le dashboard (local)

```bash
make app
# équivalent : streamlit run apps/bi-streamlit/app.py
```

## Lancer le dashboard (Docker)

```bash
docker compose up --build app
# http://localhost:8501
```

## Source du dashboard (modèle mart)

- Source principale : `marts.agg_station_latest`
- Les agrégations et indicateurs “prêts BI” sont calculés dans dbt afin de limiter la logique métier dans Streamlit (app plus simple, schéma plus stable).

## Fraîcheur des données

- Fraîcheur attendue : `validity_time_utc` ≤ 3 h (badge 🟢)
- 🟢 « À jour » : dernière `validity_time_utc` ≤ 3 h
- 🟠 « En retard » : entre 3 h et 6 h
- 🔴 « Périmé » : > 6 h

Rafraîchir manuellement : relancer l’ingestion puis `make dbt-build` (ou, en Docker, relancer les jobs `ingest` + `dbt`).

## Exposure dbt associée

Le dashboard est déclaré comme **exposure dbt** : `weather_bi_streamlit`.

Exemples :

```bash
dbt ls -s +exposure:weather_bi_streamlit
# cible uniquement les modèles qui alimentent l'exposure

dbt run -s +exposure:weather_bi_streamlit
# exécuter uniquement ce périmètre

dbt test -s +exposure:weather_bi_streamlit
# tester uniquement ce périmètre
```


## Captures

### Indicateur de fraîcheur (en retard) 
  <img src="images/dashboard-desktop-late.png" alt="Dashboard desktop retard" width="900" />

### Vue “Synthèse” (données à jour)
  <img src="images/dashboard-desktop-fresh.png" alt="Dashboard desktop frais" width="900" />


### Vue "Carte" interactive

Montre les spots filtrés sur la carte (sélection multi-onglets via les pills)
  <img src="images/dashboard-desktop-map.png" alt="Dashboard desktop frais" width="900" />



Prochaine étape (option) : [50-Orchestration-Prefect.md](50-Orchestration-Prefect.md).
