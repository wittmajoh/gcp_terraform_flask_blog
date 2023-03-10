resource "google_secret_manager_secret_iam_member" "flask_secret_member" {
  project = var.project
  secret_id = "projects/${var.project}/secrets/${var.flask_secret_key_secret_name}/versions/latest"
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.sa-cloud-run.email}"
}

resource "google_secret_manager_secret_iam_member" "database_user_password_secret_member" {
  project = var.project
  secret_id = "projects/${var.project}/secrets/${var.database_user_password_secret_name}/versions/latest"
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.sa-cloud-run.email}"
}
