FROM python:3.12-slim

WORKDIR /app

# Install dbt
COPY cloud/run/jobs/dbt/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy dbt project
COPY dbt_project.yml packages.yml /app/
COPY configs/dbt /app/configs/dbt
COPY weather_dbt /app/weather_dbt

# Default to running dbt build against BigQuery
ENV DBT_PROFILES_DIR=/app/configs/dbt

RUN dbt deps

CMD ["dbt", "build", "-t", "bigquery"]
