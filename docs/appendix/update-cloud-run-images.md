# Updating Cloud Run Images

Recommended path: keep Terraform as the source of truth and update image
digests there.

## 1. Build the image

Build only the image that changed. 

For example, for the `cloud/run/jobs/dbt` job :

```bash
gcloud config set project dbt-weather-poc

gcloud builds submit --config cloud/build/cloudbuild.dbt.yaml .
```

Other build configs:

```text
cloud/build/cloudbuild.ingest.yaml
cloud/build/cloudbuild.streamlit.yaml
```

## 2. Get the new digest

```bash
gcloud artifacts docker images describe \
  europe-west1-docker.pkg.dev/dbt-weather-poc/weather/dbt:latest \
  --format='value(image_summary.digest)'
```

## 3. Update Terraform

Replace the matching `@sha256:...` digest in:

```text
infra/cloud_run_jobs.tf
infra/cloud_run_services.tf
```

Example:

```hcl
image = "europe-west1-docker.pkg.dev/dbt-weather-poc/weather/dbt@sha256:NEW_DIGEST"
```

## 4. Apply

```bash
terraform -chdir=infra plan
terraform -chdir=infra apply
```

## 5. Verify

```bash
gcloud run jobs describe dbt-build \
  --region europe-west1 \
  --format='value(template.template.containers[0].image)'
```
