# Orchestration Prefect

Cette partie est volontairement **optionnelle** : l’objectif est de démontrer comment brancher un orchestrateur moderne autour d’un pipeline dbt existant (ingestion → dbt → DuckDB), en local.

## Raccourcis Make

- `make prefect-server` — démarre le serveur Prefect (UI : http://127.0.0.1:4200)
- `make flow-run DEPT=9` — exécute le pipeline une fois
- `make flow-serve DEPT=9` — crée/maintient un deployment + schedule horaire

## Démarrage pas à pas (local)

Terminal 1 — serveur Prefect :

```bash
make prefect-server
```

Terminal 2 — exécution ponctuelle :

```bash
make flow-run DEPT=9
```

Ou deployment horaire :

```bash
make flow-serve DEPT=9
```

Pré‑requis : `METEOFRANCE_TOKEN` disponible (même configuration que l’ingestion). Voir : [10-Setup.md](10-Setup.md)

## Mode Docker (option)

```bash
docker compose --profile prefect up --build prefect-server
docker compose --profile prefect up --build prefect
# http://localhost:4200
```

## Lecture dans l’UI Prefect

- **Deployments** : déploiements et planifications
- **Flow Runs** : historique des exécutions, états, logs, détail des tasks

## Aperçu

L’interface permet par exemple de visualiser le prochain run planifié ainsi que
l’historique des runs automatiques pour le déploiement `weather_hourly_pipeline` :

![Runs du déploiement Prefect](images/prefect-ui.png)