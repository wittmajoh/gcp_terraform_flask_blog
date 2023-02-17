# Setting up a Flask app in Google Cloud Platform using Terraform

We set up a Flask app as a Cloud Run instance using Terraform. 

The Flask app is a blog where users can post text and images. It is based on [Flaskr](https://flask.palletsprojects.com/en/2.2.x/tutorial/).

The posts and user data are stored in a Cloud SQL database. The images are stored in a storage bucket.  

![basic setting](basic_setting.drawio.svg)


## Prerequisites
We assume that [gcloud CLI](https://cloud.google.com/sdk/docs/install?hl=en) and [terraform](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli) are set up. You might need to run `gcloud auth login` and `gcloud auth application-default login` if not already done.

## Steps to set up the Flask app in GCP
1. Create a gcp project and activate billing for it.
   * Name of the project is not important.
2. Create a storage bucket.
   * Name of the bucket is not important. 
   * This bucket will be used to save the terraform state and hence can't be created by terraform itself.
3. Activate the Secret Manager API and create two secrets: 
   * A secret for the database user password. (This is part of the user credentials we will use to connect from the Flask app to the Cloud SQL database.)
   * A secret for the _SECRET_KEY_ for the Flask app.
   * Names of the secrets are not important.
   * Don't forget to fill in values for the secrets. 
4. Open [terraform.tfvars](infrastructure/terraform.tfvars).
   * Replace the value of the variable _project_ with the id of the project you created in step 1. (Note that the id of your project might be different from its name.)
   * Replace the value of the variable _bucket_name_ with the name of the storage bucket where the images will be stored. This bucket will be created and managed by terraform and is different from the bucket you created in step 1. (Choose any name you like. If you choose a name that already exists, you will get an error in step 7.)
   * Replace the values of the variables _database_user_password_secret_name_ and _flask_secret_key_secret_name_ with the secret names you chose in step 3.
5. Open [backend.tf](infrastructure/backend.tf).
   * Replace the value of the parameter _bucket_ with the name of the storage bucket you created in step 2. 
6. Deploy the docker image to the container registry:
   * In [cloudbuild.yaml](cloudbuild.yaml) replace _my-flask-app-project_ with your project id.
   * In the directory where the [cloudbuild.yaml](cloudbuild.yaml) is located, run `gcloud builds submit --project my-flask-app-project --gcs-source-staging-dir=gs://bucket-my-flask-app/blog-flask-app/
` with _my-flask-app-project_ replaced with your procejct id and _bucket-my-flask-app_ replaced with the name of the storage bucket you created in step 2.
   * If you run this for the first time, you will be asked to enable the Clould Build API. Confirm this.
7. From within the infrastructure-directory run `terraform init` followed by `terraform apply` to create the infrastructure defined by the terraform code.
   * In [main.tf](infrastructure/main.tf) the Cloud Run instance is defined. It uses the docker image we deployed in the last step.
   * This can take a while if you run this for the first time.
8. Connect to the created Cloud SQL database (e.g. by using the Cloud Shell) with the created user (username is listed in [terraform.tfvars](infrastructure/terraform.tfvars), password is the value of the secret you created). Copy and paste _schema.sql_ to create the tables.
9. The Flask App is ready to use. Navigate to the Cloud Run instance and click on its URL.

## Updating the Flask app
- If you make changes to the Flask app on the infrastructure-level (i.e. change files in the infrastructure-directory) you can deploy these changes by running `terraform apply` again. (Before you confirm, terraform will show you which resources will be changed, added or removed.)
- If you make changes to the Flask app itself (i.e. changes in the src-directory) you have to deploy the docker image again (c.f. step 6) and then build the Cloud Run instance again with `terraform apply -replace="google_cloud_run_service.cloud-run"`. (Note that simply running `terraform apply` won't suffice since terraform is not able to detect changes in the docker image.)


## Remarks
   * It is not necessary to create the secrets in step 3 manually. They can be created and managed by terraform with `resource "google_secret_manager_secret" [...]` (to create the secret) and `resource "google_secret_manager_secret_version" [...] ` (to give the secret a value). See also [this post](https://www.sethvargo.com/managing-google-secret-manager-secrets-with-terraform/) by Seth Vargo.
   * The repository was created to teach myself some basics of terraform, GCP and Flask. I would be glad if it helps others.
