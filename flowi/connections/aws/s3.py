import boto3

from flowi.settings import S3_ENDPOINT_URL


class S3(object):
    def __init__(self):
        self._s3_client = boto3.client(service_name="s3", endpoint_url=S3_ENDPOINT_URL)
        self._models_bucket = "models"

    def upload_artifact(self, local_path: str, run_id: str):
        file_name = local_path.split("/")[-1]
        s3_path = f"staging/{run_id}/{file_name}"
        self._s3_client.upload_file(local_path, self._models_bucket, s3_path)
