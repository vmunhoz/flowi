import os
from typing import Any

import mlflow

from flowi.experiment_tracking._base import Base
from flowi.utilities.logger import Logger


class MLflow(Base):

    def __init__(self, flow_name: str):
        super(MLflow, self).__init__()
        self._logger = Logger(logger_name=__name__)
        self._experiment_id = None

        self.set_experiment(flow_name=flow_name)

    def set_experiment(self, flow_name: str):
        experiment = mlflow.get_experiment_by_name(flow_name)
        if experiment:
            self._experiment_id = experiment.experiment_id
            mlflow.set_experiment(flow_name)
        else:
            self._experiment_id = mlflow.create_experiment(flow_name)

    def start_run(self):
        mlflow.start_run(experiment_id=self._experiment_id)

    @staticmethod
    def end_run():
        mlflow.end_run()

    @staticmethod
    def set_param(key: str, value: str or int or float):
        mlflow.log_param(key=key, value=value)

    @staticmethod
    def set_metric(key: str, value: str or int or float):
        mlflow.log_metric(key=key, value=value)

    def save_transformer(self, obj: Any, file_path: str):
        artifact_path = 'transformers'
        file_path = self._save_pickle(obj=obj, file_path=file_path)

        file_name = os.path.basename(file_path)
        mlflow.log_artifact(local_path=file_path, artifact_path=artifact_path)
        artifact_uri = mlflow.get_artifact_uri(artifact_path=os.path.join(artifact_path, file_name))
        self._logger.debug(artifact_uri)

        return artifact_uri.replace('file://', '')

    def save_model(self, obj: Any, file_path: str):
        artifact_path = 'models'
        file_path = self._save_pickle(obj=obj, file_path=file_path)

        file_name = os.path.basename(file_path)
        mlflow.log_artifact(local_path=file_path, artifact_path=artifact_path)
        artifact_uri = mlflow.get_artifact_uri(artifact_path=os.path.join(artifact_path, file_name))
        self._logger.debug(artifact_uri)

        return artifact_uri.replace('file://', '')
