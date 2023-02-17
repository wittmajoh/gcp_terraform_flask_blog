import os
from google.cloud import storage

BUCKET_NAME = os.environ.get("BUCKET_NAME")


storage_client = storage.Client()


def create_blob(blob_name):
    """
    Create an object (blob) with name "blob_name" in the storage bucket.
    """
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    return blob


def upload_img_to_blob(img, blob):
    """
    Upload the image to the (existing) blob.
    """
    blob.upload_from_string(img.read(), content_type=img.content_type)
    blob.make_public()
    return blob.public_url


def delete_blob(blob_name):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.delete()
