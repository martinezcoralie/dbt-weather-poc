resource "google_service_account" "cr_job_ingest" {
  account_id   = "cr-job-ingest"
  display_name = "cr-job-ingest"
}

resource "google_service_account" "cr_job_dbt" {
  account_id   = "cr-job-dbt"
  display_name = "cr-job-dbt"
}

resource "google_service_account" "cr_svc_streamlit" {
  account_id   = "cr-svc-streamlit"
  display_name = "cr-svc-streamlit"
}
