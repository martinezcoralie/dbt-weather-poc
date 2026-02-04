# --- BigQuery permissions (minimal) ---

# Ingest job: writes to raw tables
resource "google_project_iam_member" "ingest_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}

resource "google_project_iam_member" "ingest_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}

# dbt job: writes to staging/intermediate/marts
resource "google_project_iam_member" "dbt_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cr_job_dbt.email}"
}

resource "google_project_iam_member" "dbt_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cr_job_dbt.email}"
}

# Streamlit service: reads from marts (and runs queries)
resource "google_project_iam_member" "streamlit_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cr_svc_streamlit.email}"
}

resource "google_project_iam_member" "streamlit_bq_data_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.cr_svc_streamlit.email}"
}
