terraform {
  backend "gcs" {
    bucket = "bucket-my-flask-app" # storage bucket where the terraform state will be saved
    prefix = "terraform/state"
  }
}