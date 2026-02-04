resource "google_cloud_run_v2_job" "ingest" {
  name     = "ingest-obs-hourly"
  location = var.region

  template {
    template {
      service_account = google_service_account.cr_job_ingest.email

      containers {
        image = "europe-west1-docker.pkg.dev/dbt-weather-poc/weather/ingest:latest"

        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        env {
          name  = "BQ_DATASET"
          value = "raw"
        }

        env {
          name  = "BQ_TARGET_TABLE"
          value = "obs_hourly"
        }
        env {
          name  = "BQ_STAGING_TABLE"
          value = "_obs_hourly_staging"
        }
        env {
          name  = "DEPT_CODE"
          value = "09"
        }

        env {
          name = "METEOFRANCE_TOKEN"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.meteofrance_token.secret_id
              version = "1"
            }
          }
        }
      }
    }
  }
}
