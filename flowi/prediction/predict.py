from typing import List
from pickle import load, loads
import numpy as np
import boto3
from botocore.client import Config

from flowi.settings import MLFLOW_S3_ENDPOINT_URL
from flowi.utilities.imports import import_class
import dask.dataframe as dd


def _load_from_file(pickle_path: str):
    pickle_path = pickle_path.replace("file://", "")
    return load(open(pickle_path, "rb"))


def _load_from_s3(pickle_path: str):
    pickle_path = pickle_path.replace("s3://", "")
    bucket = pickle_path.split("/")[0]
    s3_path = pickle_path.replace(bucket + "/", "")

    s3 = boto3.resource("s3", endpoint_url=MLFLOW_S3_ENDPOINT_URL, config=Config(signature_version="s3v4"))

    s3_response_object = s3.meta.client.get_object(Bucket=bucket, Key=s3_path)
    return loads(s3_response_object["Body"].read())


def _load_transformer(pickle_path: str):
    if pickle_path.startswith("file://"):
        return _load_from_file(pickle_path=pickle_path)
    elif pickle_path.startswith("s3://"):
        return _load_from_s3(pickle_path=pickle_path)


def predict(x: dd.DataFrame or np.array, prediction_flow: List[dict]):
    if not isinstance(x, dd.DataFrame):
        df = dd.from_array(x=x)
    else:
        df = x

    for step in prediction_flow:
        component_class = import_class(step["class_name"])()
        if step["pickle"] is None:
            kwargs = step["kwargs"]
            result = component_class.apply(
                method_name=step["method_name"], shared_variables={"df": df}, node_attributes=kwargs
            )
            df = result["df"]
        else:
            transformer = _load_transformer(step["pickle"])
            if "model" not in step["class_name"]:
                df = transformer.transform()
            else:
                return transformer.predict(df.values)

    raise BrokenPipeError("Missing model to predict")
