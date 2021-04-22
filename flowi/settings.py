import os


def _get_env(variable_name: str):
    return os.environ.get(variable_name)


def _unset_variable(variable_name: str):
    if variable_name in os.environ:
        del os.environ[variable_name]


FLOW_NAME = _get_env(variable_name='FLOW_NAME')
EXPERIMENT_TRACKING = _get_env(variable_name='EXPERIMENT_TRACKING')
