resource "google_secret_manager_secret" "meteofrance_token" {
  secret_id = "METEOFRANCE_TOKEN"

  replication {
    auto {}
  }
}
