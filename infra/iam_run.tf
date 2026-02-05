
resource "google_cloud_run_service_iam_member" "streamlit_public" {
  project  = var.project_id
  location = var.region
  service  = "streamlit"
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_job_iam_member" "ingest_job_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.ingest.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}

resource "google_cloud_run_v2_job_iam_member" "dbt_job_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.dbt_build.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cr_job_dbt.email}"
}
