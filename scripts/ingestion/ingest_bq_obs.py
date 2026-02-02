"""Ingest hourly observations into BigQuery (raw.obs_hourly)."""

import time

import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

from scripts.ingestion.fetch_meteofrance_paquetobs import (
    open_session_paquetobs,
    fetch_hourly_for_dept,
)
from scripts.ingestion.utils import env, now_utc_iso, setup_logging

# --------- ENV VARS (required) ---------

PROJECT_ID = env("GCP_PROJECT")
DATASET = env("BQ_DATASET", "raw")
TARGET_TABLE = env("BQ_TARGET_TABLE", "obs_hourly")
STAGING_TABLE = env("BQ_STAGING_TABLE", "_obs_hourly_staging")
DEPT = env("DEPT_CODE", "09")

# --------- LOGGING ------------
logger = setup_logging(__name__)

# ------------------------------


def main():
    """Fetch hourly observations and merge into a partitioned BigQuery table."""
    t0 = time.time()

    logger.info("start dept=%s project=%s dataset=%s", DEPT, PROJECT_ID, DATASET)

    # 1) Fetch hourly observations for the department.
    session = open_session_paquetobs()
    df = fetch_hourly_for_dept(session, DEPT)

    logger.info("fetched rows=%s stations=%s", len(df), df["geo_id_insee"].nunique())

    # Parse and derive partitioning columns.
    df["validity_time"] = pd.to_datetime(df["validity_time"], utc=True, errors="coerce")
    df["validity_date"] = df["validity_time"].dt.date

    # 2) Add a load timestamp for traceability.
    df["load_time"] = now_utc_iso()

    client = bigquery.Client(project=PROJECT_ID)

    staging_id = f"{PROJECT_ID}.{DATASET}.{STAGING_TABLE}"
    target_id = f"{PROJECT_ID}.{DATASET}.{TARGET_TABLE}"

    # 3) Load into staging (truncate first).
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    load_job = client.load_table_from_dataframe(df, staging_id, job_config=job_config)
    load_job.result()

    logger.info("loaded staging=%s", staging_id)

    # 4) Ensure target table exists and is partitioned.
    try:
        client.get_table(target_id)
        logger.info(
            "target exists=%s; (drop to recreate)",
            target_id,
        )
    except NotFound:
        staging_table = client.get_table(staging_id)
        target_table = bigquery.Table(target_id, schema=staging_table.schema)
        target_table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="validity_date",
        )
        client.create_table(target_table)
        logger.info("created target=%s partitioned by validity_date", target_id)

    # 5) Merge staging into target (insert new rows only).
    merge_sql = f"""
    MERGE `{target_id}` T
    USING `{staging_id}` S
    ON  T.validity_time  = S.validity_time
    AND T.geo_id_insee   = S.geo_id_insee
    AND T.reference_time = S.reference_time
    WHEN NOT MATCHED THEN
      INSERT ROW
    """

    client.query(merge_sql).result()

    logger.info("merged into target=%s", target_id)

    logger.info("done duration_s=%.2f", time.time() - t0)


if __name__ == "__main__":
    main()
