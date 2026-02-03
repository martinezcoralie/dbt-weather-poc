"""Local Prefect flow: Météo-France ingestion → dbt build (DuckDB)."""

from pathlib import Path
import os
import subprocess
import time

from prefect import flow, task
import httpx


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(cmd: str) -> None:
    """
    Helper to run a shell command from the project root,
    with direct log output and a clear error on failure.
    """
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=PROJECT_ROOT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with code {result.returncode}: {cmd}")


def wait_for_prefect_api(timeout_s: int = 60, interval_s: float = 2.0) -> None:
    """Wait for Prefect API to be reachable before registering a deployment."""
    api_url = os.getenv("PREFECT_API_URL", "http://127.0.0.1:4200/api")
    health_url = f"{api_url.rstrip('/')}/health"
    deadline = time.time() + timeout_s
    last_err: Exception | None = None

    while time.time() < deadline:
        try:
            resp = httpx.get(health_url, timeout=5)
            if resp.status_code == 200:
                return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
        time.sleep(interval_s)

    raise RuntimeError(f"Prefect API not reachable: {health_url}") from last_err


@task
def ingest_meteofrance(dept: int = 9) -> None:
    """
    Prefect task: ingest raw data from the Météo-France API into DuckDB
    via the Makefile.
    """
    cmd = f"make dwh-ingest DEPT={dept}"
    run_cmd(cmd)


@task
def run_dbt_build() -> None:
    """
    Prefect task: run dbt (deps + build) for the project.
    """
    cmd = "make dbt-build"
    run_cmd(cmd)


@flow(name="weather-hourly-pipeline")
def weather_hourly_pipeline(dept: int = 9) -> None:
    """
    Prefect flow: chain ingestion + dbt build.
    """
    ingest_meteofrance(dept)
    run_dbt_build()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Weather pipeline orchestrated with Prefect"
    )
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
        wait_for_prefect_api()
        weather_hourly_pipeline.serve(
            name="weather-hourly-deployment",
            cron="0 * * * *",  # toutes les heures à minute 0
            tags=["weather", "hourly", "demo"],
            pause_on_shutdown=True,  # auto-pause le schedule si on stoppe le process
        )
