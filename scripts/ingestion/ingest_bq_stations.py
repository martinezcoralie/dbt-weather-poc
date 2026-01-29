import time

from google.cloud import bigquery

from scripts.ingestion.fetch_meteofrance_paquetobs import (
    open_session_paquetobs,
    fetch_stations,
)
from scripts.ingestion.utils import env, now_utc_iso, setup_logging

# --------- ENV VARS (required) ---------

PROJECT_ID = env("GCP_PROJECT")
DATASET = env("BQ_DATASET", "raw")
TARGET_TABLE = env("BQ_TARGET_TABLE", "stations")

# --------- LOGGING ------------
logger = setup_logging(__name__)


def main():
    t0 = time.time()

    logger.info(
        "start project=%s dataset=%s table=%s", PROJECT_ID, DATASET, TARGET_TABLE
    )

    # 1) Fetch stations from MeteoFrance API.
    session = open_session_paquetobs()
    df = fetch_stations(session)

    # trace ingestion
    df["load_time"] = now_utc_iso()

    logger.info("fetched stations=%s, cols=%s", len(df), df.shape[1])

    client = bigquery.Client(project=PROJECT_ID)

    target_id = f"{PROJECT_ID}.{DATASET}.{TARGET_TABLE}"

    # 3) Load into target (truncate first).
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    load_job = client.load_table_from_dataframe(df, target_id, job_config=job_config)
    load_job.result()

    logger.info("loaded target=%s rows=%d", target_id, len(df))

    logger.info("done duration_s=%.2f", time.time() - t0)


if __name__ == "__main__":
    main()
