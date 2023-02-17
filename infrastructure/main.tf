locals {
  service_name = "blog-flask-app"
}

resource "google_cloud_run_service" "cloud-run" {
  name                       = local.service_name
  location                   = var.region
  autogenerate_revision_name = true

  template {
    spec {
      timeout_seconds = 3600
      containers {
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
        image = "eu.gcr.io/${var.project}/${local.service_name}:latest"
        # make variable names and secret values accessible in the source code. They will be called in the python code via "os.environ.get(...)".
        env {
          name  = "BUCKET_NAME"
          value = var.bucket_name
        }
        env {
          name  = "DATABASE"
          value = google_sql_database.database.name
        }
        env {
          name  = "CLOUD_SQL_CONNECTION_NAME"
          value = "${var.project}:${var.region}:${google_sql_database_instance.instance.name}"
        }
        env {
          name  = "DATABASE_USER_NAME"
          value = var.database_user_name
        }
        env {
          name = "FLASK_SECRET_KEY"
          value_from {
            secret_key_ref {
              name = data.google_secret_manager_secret.flask_secret.secret_id
              key  = "latest"
            }
          }
        }
        env {
          name = "DATABASE_USER_PASSWORD"
          value_from {
            secret_key_ref {
              name = data.google_secret_manager_secret.database_user_password_secret.secret_id
              key  = "latest"
            }
          }
        }
      }
      service_account_name = google_service_account.sa-cloud-run.email
    }
    metadata {
      annotations = {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.instance.connection_name 
        # c.f. https://cloud.google.com/sql/docs/mysql/connect-run?hl=en#terraform
      }
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
  depends_on = [
    google_service_account.sa-cloud-run,
    google_project_iam_member.editor,
    google_project_service.run-api,
    google_sql_database_instance.instance,
    google_sql_database.database,
    google_secret_manager_secret_iam_member.flask_secret_member,
    google_secret_manager_secret_iam_member.database_user_password_secret_member
  ]
}

resource "google_service_account" "sa-cloud-run" {
  display_name = "${local.service_name}-sa"
  account_id   = "${local.service_name}-sa"
  project      = var.project
}

resource "google_project_iam_member" "editor" {
  project = var.project
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.sa-cloud-run.email}"
}

resource "google_project_service" "run-api" {
  service = "run.googleapis.com"

  disable_on_destroy = true
}

# make the cloud run instance accessible for anyone on the internet
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers", # represents anyone on the internet 
    ]
  }
  
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.cloud-run.location
  project     = google_cloud_run_service.cloud-run.project
  service     = google_cloud_run_service.cloud-run.name

  policy_data = data.google_iam_policy.noauth.policy_data
  
}