# bucket to store the images
resource "google_storage_bucket" "bucket" {
  name = var.bucket_name
  location = var.region
}

resource "google_storage_bucket_iam_member" "bucket" {
  bucket = google_storage_bucket.bucket.name
  role = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.sa-cloud-run.email}"
}