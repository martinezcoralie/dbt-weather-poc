
resource "google_cloud_run_service_iam_member" "streamlit_public" {
  project  = var.project_id
  location = var.region
  service  = "streamlit"
  role     = "roles/run.invoker"
  member   = "allUsers"
}
