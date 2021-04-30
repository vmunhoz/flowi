from typing import List
from pickle import load, loads
import numpy as np
import boto3
from botocore.client import Config

from flowi.settings import MLFLOW_S3_ENDPOINT_URL
import dask.dataframe as dd
from sklearn.pipeline import Pipeline


class Predict(object):
    def __init__(self, prediction_flow: List[dict]):
        self._transformer, self._model = self._setup(prediction_flow=prediction_flow)

    def _setup(self, prediction_flow):
        steps = []
        model = None
        for i, step in enumerate(prediction_flow):
            transformer = self._load_transformer(step["pickle"])
            if "model" not in step["class_name"]:
                steps.append((f"transformer{i}", transformer))
            else:
                model = transformer

        return Pipeline(steps), model

    @staticmethod
    def _load_from_file(pickle_path: str):
        pickle_path = pickle_path.replace("file://", "")
        return load(open(pickle_path, "rb"))

    @staticmethod
    def _load_from_s3(pickle_path: str):
        pickle_path = pickle_path.replace("s3://", "")
        bucket = pickle_path.split("/")[0]
        s3_path = pickle_path.replace(bucket + "/", "")

        s3 = boto3.resource("s3", endpoint_url=MLFLOW_S3_ENDPOINT_URL, config=Config(signature_version="s3v4"))

        s3_response_object = s3.meta.client.get_object(Bucket=bucket, Key=s3_path)
        return loads(s3_response_object["Body"].read())

    def _load_transformer(self, pickle_path: str):
        if pickle_path.startswith("file://"):
            return self._load_from_file(pickle_path=pickle_path)
        elif pickle_path.startswith("s3://"):
            return self._load_from_s3(pickle_path=pickle_path)

    @staticmethod
    def _to_df(X: dd.DataFrame or np.ndarray):
        if not isinstance(X, dd.DataFrame):
            df = dd.from_array(x=X)
        else:
            df = X

        return df

    def transform_input(self, X: dd.DataFrame or np.ndarray):
        X = self._to_df(X)
        return self._transformer.transform(X)

    def predict(self, X: dd.DataFrame or np.ndarray):
        X = self._to_df(X)
        return self._model.predict(X)


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
#
#
# def predict(x: dd.DataFrame or np.array, prediction_flow: List[dict]):
#     if not isinstance(x, dd.DataFrame):
#         df = dd.from_array(x=x)
#     else:
#         df = x
#
#     for step in prediction_flow:
#         component_class = import_class(step["class_name"])()
#         if step["pickle"] is None:
#             kwargs = step["kwargs"]
#             result = component_class.apply(
#                 method_name=step["method_name"], shared_variables={"df": df}, node_attributes=kwargs
#             )
#             df = result["df"]
#         else:
#             transformer = _load_transformer(step["pickle"])
#             if "model" not in step["class_name"]:
#                 df = transformer.transform(df)
#             else:
#                 return transformer.predict(df.values)
#
#     raise BrokenPipeError("Missing model to predict")
