FROM python:3.12-slim

WORKDIR /app
COPY cloud/run/job/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY scripts/__init__.py /app/scripts/__init__.py
COPY scripts/ingestion /app/scripts/ingestion

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "scripts.ingestion.ingest_bq_obs"]
