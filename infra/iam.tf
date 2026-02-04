resource "google_project_iam_member" "cr_ingest_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}

resource "google_project_iam_member" "cr_ingest_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}

resource "google_project_iam_member" "cr_ingest_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}


resource "google_secret_manager_secret_iam_member" "cr_ingest_secret_access" {
  secret_id = google_secret_manager_secret.meteofrance_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}
