from datetime import datetime, timezone
import os

import pandas as pd
from google.cloud import bigquery

from scripts.ingestion.fetch_meteofrance_paquetobs import (
    open_session_paquetobs,
    fetch_hourly_for_dept,
)

PROJECT_ID = "dbt-weather-poc"
DATASET = "raw"
TARGET_TABLE = "obs_hourly"
STAGING_TABLE = "_obs_hourly_staging"
DEPT = "9"


def main():
    # 1) Fetch API
    session = open_session_paquetobs()
    df = fetch_hourly_for_dept(session, DEPT)

    # 2) Add load_time
    df["load_time"] = datetime.now(timezone.utc).isoformat()

    client = bigquery.Client(project=PROJECT_ID)

    staging_id = f"{PROJECT_ID}.{DATASET}.{STAGING_TABLE}"
    target_id = f"{PROJECT_ID}.{DATASET}.{TARGET_TABLE}"

    # 3) Load staging (truncate)
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    load_job = client.load_table_from_dataframe(
        df, staging_id, job_config=job_config
    )
    load_job.result()

    # 4) Merge staging → target
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

    print(f"OK - rows fetched: {len(df)}")


if __name__ == "__main__":
    main()
