resource "google_cloud_scheduler_job" "ingest" {
  name        = "sched-ingest"
  description = "Trigger Cloud Run Job ingest"
  project     = "dbt-weather-poc"
  region      = "europe-west1"

  # Ingest first, then dbt a few minutes later.
  schedule  = "5 */2 * * *"
  time_zone = "Europe/Paris"

  attempt_deadline = "180s"

  retry_config {
    min_backoff_duration = "5s"
    max_backoff_duration = "3600s"
    max_doublings        = 5
    max_retry_duration   = "0s"
  }

  http_target {
    http_method = "POST"
    uri         = "https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/372280565516/jobs/ingest-obs-hourly:run"

    oauth_token {
      service_account_email = "cr-job-ingest@dbt-weather-poc.iam.gserviceaccount.com"
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}

resource "google_cloud_scheduler_job" "dbt_build" {
  name        = "sched-dbt-build"
  description = "Trigger Cloud Run Job dbt-build"
  project     = "dbt-weather-poc"
  region      = "europe-west1"

  # Runs after ingest.
  schedule  = "10 */2 * * *"
  time_zone = "Europe/Paris"

  attempt_deadline = "180s"

  retry_config {
    min_backoff_duration = "5s"
    max_backoff_duration = "3600s"
    max_doublings        = 5
    max_retry_duration   = "0s"
  }

  http_target {
    http_method = "POST"
    uri         = "https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/372280565516/jobs/dbt-build:run"

    oauth_token {
      service_account_email = "cr-job-dbt@dbt-weather-poc.iam.gserviceaccount.com"
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}
