resource "google_secret_manager_secret_iam_member" "cr_ingest_secret_access" {
  secret_id = google_secret_manager_secret.meteofrance_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cr_job_ingest.email}"
}