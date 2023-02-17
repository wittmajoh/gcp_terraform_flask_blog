
# make the manually created secrets usable by terraform by loading them as data
data "google_secret_manager_secret" "flask_secret" {
  secret_id = var.flask_secret_key_secret_name
}

data "google_secret_manager_secret" "database_user_password_secret" {
  secret_id = var.database_user_password_secret_name
}

resource "google_secret_manager_secret_iam_member" "flask_secret_member" {
  project = var.project
  secret_id = data.google_secret_manager_secret.flask_secret.secret_id
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.sa-cloud-run.email}"
  depends_on = [
    data.google_secret_manager_secret.flask_secret
  ]
}

resource "google_secret_manager_secret_iam_member" "database_user_password_secret_member" {
  project = var.project
  secret_id = data.google_secret_manager_secret.database_user_password_secret.secret_id
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.sa-cloud-run.email}"
  depends_on = [
    data.google_secret_manager_secret.database_user_password_secret
  ]
}
