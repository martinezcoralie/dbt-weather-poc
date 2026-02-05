resource "google_cloud_run_v2_service" "streamlit" {
  name     = "streamlit"
  location = "europe-west1"
  project  = "dbt-weather-poc"

  # Public ingress; IAM in iam_run.tf grants allUsers for this service.
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = "cr-svc-streamlit@dbt-weather-poc.iam.gserviceaccount.com"

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    # Keep costs down while staying responsive for a small dashboard.
    timeout                          = "300s"
    max_instance_request_concurrency = 80

    containers {
      name  = "streamlit-1"
      image = "europe-west1-docker.pkg.dev/dbt-weather-poc/weather/streamlit@sha256:500f931c6bb2a725aea821c56929eeb20c32a4235d377653825c321337d60faf"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }

      env {
        name  = "BQ_DATASET"
        value = "marts"
      }
      env {
        name  = "BQ_PROJECT"
        value = "dbt-weather-poc"
      }
      env {
        name  = "BQ_TABLE"
        value = "agg_station_latest"
      }
      env {
        name  = "DATA_BACKEND"
        value = "bigquery"
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100

  }
}
