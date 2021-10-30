from abc import abstractmethod
from typing import Any

import dill


class Base(object):
    def __init__(self, flow_name: str, version: str):
        pass

    def set_project(self, flow_name: str):
        pass

    def start_experiment(self) -> str:
        pass

    def end_experiment(self, experiment_id: str):
        pass

    def log_param(self, experiment_id: str, key: str, value: str or int or float):
        pass

    def log_metric(self, experiment_id: str, key: str, value: str or int or float):
        pass

    def save_transformer(self, experiment_id: str, obj: Any, file_path: str):
        pass

    def save_columns(self, experiment_id: str, obj: Any, file_path: str):
        pass

    def save_drift(self, experiment_id: str, file_path: str):
        pass

    def save_model(self, experiment_id: str, obj: Any, file_path: str):
        pass

    def download_artifact(self, artifact_uri: str) -> str:
        pass

    @staticmethod
    def _save_pickle(obj: Any, file_path: str) -> str:
        file_path = file_path if file_path.endswith(".pkl") else file_path + ".pkl"
        with open(file_path, "wb") as f:
            dill.dump(obj=obj, file=f)

        return file_path
