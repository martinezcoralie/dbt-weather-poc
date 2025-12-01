from pathlib import Path
import subprocess

from prefect import flow, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(cmd: str) -> None:
    """
    Helper pour exécuter une commande shell depuis la racine du projet,
    avec affichage des logs en direct et erreur explicite en cas d'échec.
    """
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=PROJECT_ROOT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with code {result.returncode}: {cmd}")


@task
def ingest_meteofrance(dept: int = 9) -> None:
    """
    Tâche Prefect : ingestion des données brutes depuis l’API Météo-France
    vers DuckDB, via le Makefile.
    """
    cmd = f"make dwh-ingest DEPT={dept}"
    run_cmd(cmd)


@task
def run_dbt_build() -> None:
    """
    Tâche Prefect : exécution de dbt (deps + build) sur le projet.
    """
    cmd = "DBT_PROFILES_DIR=profiles dbt deps && DBT_PROFILES_DIR=profiles dbt build"
    run_cmd(cmd)


@flow(name="weather-hourly-pipeline")
def weather_hourly_pipeline(dept: int = 9) -> None:
    """
    Flow Prefect : enchaîne ingestion + dbt build.

    Pour l’instant, on le lance “à la main”.
    Plus tard, on le transformera en déploiement avec un schedule (horaire).
    """
    ingest_meteofrance(dept)
    run_dbt_build()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Weather pipeline orchestrated with Prefect")
    parser.add_argument(
        "--mode",
        choices=["run", "serve"],
        default="run",
        help="run = exécuter une fois ; serve = créer un deployment + schedule et écouter les runs",
    )
    parser.add_argument(
        "--dept",
        type=int,
        default=9,
        help="Code département Météo-France (ex : 9 pour Ariège)",
    )

    args = parser.parse_args()

    if args.mode == "run":
        # Exécution simple
        weather_hourly_pipeline(dept=args.dept)

    elif args.mode == "serve":
        # Crée un deployment + schedule cron (toutes les heures)
        # et démarre un process long qui écoute les runs planifiés.
        weather_hourly_pipeline.serve(
            name="weather-hourly-deployment",
            cron="0 * * * *",  # toutes les heures à minute 0
            tags=["weather", "hourly", "demo"],
            pause_on_shutdown=True,  # auto-pause le schedule si on stoppe le process
        )
