import logging
import os


def _get_env(variable_name: str, default=None):
    return os.environ.get(key=variable_name, default=default)


def _unset_variable(variable_name: str):
    if variable_name in os.environ:
        del os.environ[variable_name]


FLOW_NAME = _get_env(variable_name="FLOW_NAME")
VERSION = _get_env(variable_name="VERSION", default="not versioned")
EXPERIMENT_TRACKING = _get_env(variable_name="EXPERIMENT_TRACKING")
MLFLOW_S3_ENDPOINT_URL = _get_env(variable_name="MLFLOW_S3_ENDPOINT_URL")
MONGO_ENDPOINT_URL = _get_env(variable_name="MONGO_ENDPOINT_URL")
LOG_LEVEL = _get_env(variable_name="LOG_LEVEL", default=logging.INFO)
