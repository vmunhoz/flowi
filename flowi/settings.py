import logging
import os


def _get_env(variable_name: str, default=None):
    return os.environ.get(key=variable_name, default=default)


def _unset_variable(variable_name: str):
    if variable_name in os.environ:
        del os.environ[variable_name]


FLOW_NAME = _get_env(variable_name='FLOW_NAME')
EXPERIMENT_TRACKING = _get_env(variable_name='EXPERIMENT_TRACKING')
LOG_LEVEL = _get_env(variable_name='LOG_LEVEL', default=logging.INFO)
