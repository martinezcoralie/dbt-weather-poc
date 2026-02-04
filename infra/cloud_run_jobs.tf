resource "google_cloud_run_v2_job" "ingest" {
  name     = "ingest-obs-hourly"
  location = var.region

  template {
    template {
      service_account = google_service_account.cr_job_ingest.email
      max_retries     = 1

      containers {
        name  = "ingest-1"
        image = "europe-west1-docker.pkg.dev/dbt-weather-poc/weather/ingest@sha256:fbe8989914f2df1042e5120b2752d71096f9fa6cbf00541296604ce7f3cad10e"
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

resource "google_cloud_run_v2_job" "stations" {
  name     = "ingest-stations"
  location = var.region

  template {
    template {
      service_account = google_service_account.cr_job_ingest.email
      max_retries     = 1

      containers {
        name  = "ingest-1"
        image = "europe-west1-docker.pkg.dev/dbt-weather-poc/weather/ingest@sha256:fbe8989914f2df1042e5120b2752d71096f9fa6cbf00541296604ce7f3cad10e"
        args = ["-m", "scripts.ingestion.ingest_bq_stations",
        ]
        command = [
          "python",
        ]
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
          value = "stations"
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

resource "google_cloud_run_v2_job" "dbt_build" {
  name     = "dbt-build"
  location = var.region

  template {
    template {
      service_account = google_service_account.cr_job_dbt.email
      max_retries     = 1

      containers {
        name  = "ingest-1"
        image = "europe-west1-docker.pkg.dev/dbt-weather-poc/weather/dbt@sha256:fbfbeacb7901a341574f47e533df12324f4e659b5b6055a55005f7777d361c21"



      }
    }
  }
}