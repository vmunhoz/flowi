import logging
import os
import uuid


def _get_env(variable_name: str, default=None):
    return os.environ.get(key=variable_name, default=default)


def _unset_variable(variable_name: str):
    if variable_name in os.environ:
        del os.environ[variable_name]


FLOW_NAME = _get_env(variable_name="FLOW_NAME", default="unknown")
VERSION = _get_env(variable_name="VERSION", default="not versioned")
RUN_ID = _get_env(variable_name="RUN_ID", default=str(uuid.uuid4()))
EXPERIMENT_TRACKING = _get_env(variable_name="EXPERIMENT_TRACKING", default="MLflow")
S3_ENDPOINT_URL = _get_env(variable_name="MLFLOW_S3_ENDPOINT_URL")
FLOWI_BUCKET = _get_env(variable_name="FLOWI_BUCKET", default="flowi")
MONGO_ENDPOINT_URL = _get_env(variable_name="MONGO_ENDPOINT_URL", default="localhost")
DASK_SCHEDULER = _get_env(variable_name="DASK_SCHEDULER", default=None)
LOG_LEVEL = _get_env(variable_name="LOG_LEVEL", default="INFO")
