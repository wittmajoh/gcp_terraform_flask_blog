resource "google_sql_database_instance" "instance" {
  name             = "database-instance"
  database_version = "MYSQL_8_0"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    backup_configuration  {
        enabled    = true
        start_time = "00:00"
    }

    deletion_protection_enabled = true # the GCP deletion protection feature

  }

  deletion_protection = true # the terraform deletion protection feature (i.e. "terraform apply/destroy" can not destroy it)
}

resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.instance.name
}

# make the value of the created secret available by loading its latest version 
data "google_secret_manager_secret_version" "database_user_password" {
  secret = var.database_user_password_secret_name
  version = "latest"
}

resource "google_sql_user" "user" {
  name     = var.database_user_name
  instance = google_sql_database_instance.instance.name
  password = data.google_secret_manager_secret_version.database_user_password.secret_data
}

resource "google_project_service" "sql-admin-api" {
  service = "sqladmin.googleapis.com"
}

resource "google_project_iam_member" "cloudsql" {
  project = var.project
  role    = "roles/cloudsql.editor"
  member  = "serviceAccount:${google_service_account.sa-cloud-run.email}"
}


