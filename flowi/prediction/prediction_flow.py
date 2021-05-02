# from pickle import load, loads
from typing import List

# import boto3
# from botocore.client import Config
from sklearn.pipeline import Pipeline

# from flowi.settings import MLFLOW_S3_ENDPOINT_URL

#
# def _load_from_file(pickle_path: str):
#     pickle_path = pickle_path.replace("file://", "")
#     return load(open(pickle_path, "rb"))
#
#
# def _load_from_s3(pickle_path: str):
#     pickle_path = pickle_path.replace("s3://", "")
#     bucket = pickle_path.split("/")[0]
#     s3_path = pickle_path.replace(bucket + "/", "")
#
#     s3 = boto3.resource("s3", endpoint_url=MLFLOW_S3_ENDPOINT_URL, config=Config(signature_version="s3v4"))
#
#     s3_response_object = s3.meta.client.get_object(Bucket=bucket, Key=s3_path)
#     return loads(s3_response_object["Body"].read())
#
#
# def _load_transformer(pickle_path: str):
#     if pickle_path.startswith("file://"):
#         return _load_from_file(pickle_path=pickle_path)
#     elif pickle_path.startswith("s3://"):
#         return _load_from_s3(pickle_path=pickle_path)


def _create_pipeline(transformers: list) -> Pipeline or None:
    steps = []
    for i, transformer in enumerate(transformers):
        steps.append((f"transformer{i}", transformer))
    if steps:
        return Pipeline(steps)
    else:
        return None


def create_transform_pipeline(prediction_flow: List[dict], transform_type: str) -> Pipeline or None:
    """
    Create a transform pipeline for preprocessing (transform_input) or post_processing/decode (transform_output)
    :param prediction_flow: Dictionary with prediction steps (transformers)
    :type transform_type: Either transform_input or transform_output
    """
    filtered_transformers = []
    for i, step in enumerate(prediction_flow):
        if transform_type in step and step[transform_type]:
            filtered_transformers.append(step["object"])

    pipeline = _create_pipeline(filtered_transformers)
    return pipeline
