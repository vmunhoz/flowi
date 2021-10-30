import os
from typing import Any

import mlflow

from flowi.experiment_tracking._base import Base
from flowi.utilities.logger import Logger
from mlflow.tracking import MlflowClient


class MLflow(Base):
    def __init__(self, flow_name: str, version: str):
        super(MLflow, self).__init__(flow_name=flow_name, version=version)
        self._logger = Logger(logger_name=__name__)
        self._client = MlflowClient()
        self._version = version
        self._experiment_id = None

        self.set_project(flow_name=flow_name)

    def set_project(self, flow_name: str):
        project = mlflow.get_experiment_by_name(flow_name)
        if project:
            self._experiment_id = project.experiment_id
            mlflow.set_experiment(flow_name)
        else:
            self._experiment_id = mlflow.create_experiment(flow_name)

    def start_experiment(self) -> str:
        run = self._client.create_run(experiment_id=self._experiment_id, tags={"version": self._version})
        return run.info.run_id

    def end_experiment(self, experiment_id: str):
        self._client.set_terminated(run_id=experiment_id)

    def log_param(self, experiment_id: str, key: str, value: str or int or float):
        self._client.log_param(run_id=experiment_id, key=key, value=value)

    def log_metric(self, experiment_id: str, key: str, value: str or int or float):
        self._client.log_metric(run_id=experiment_id, key=key, value=value)

    def _save_artefact(self, experiment_id: str, obj: Any, file_path: str, artifact_path: str) -> str:
        file_path = self._save_pickle(obj=obj, file_path=file_path)

        file_name = os.path.basename(file_path)
        self._client.log_artifact(run_id=experiment_id, local_path=file_path, artifact_path=artifact_path)

        run = self._client.get_run(run_id=experiment_id)
        artifact_uri = os.path.join(run.info.artifact_uri, artifact_path, file_name)

        self._logger.debug(artifact_uri)

        return artifact_uri

    def _save_file(self, experiment_id: str, file_path: str, artifact_path: str) -> str:
        file_name = os.path.basename(file_path)
        self._client.log_artifact(run_id=experiment_id, local_path=file_path, artifact_path=artifact_path)

        run = self._client.get_run(run_id=experiment_id)
        artifact_uri = os.path.join(run.info.artifact_uri, artifact_path, file_name)

        self._logger.debug(artifact_uri)

        return artifact_uri

    def save_transformer(self, experiment_id: str, obj: Any, file_path: str) -> str:
        artifact_path = "transformers"
        return self._save_artefact(
            experiment_id=experiment_id, obj=obj, file_path=file_path, artifact_path=artifact_path
        )

    def save_columns(self, experiment_id: str, obj: Any, file_path: str) -> str:
        artifact_path = "columns"
        return self._save_artefact(
            experiment_id=experiment_id, obj=obj, file_path=file_path, artifact_path=artifact_path
        )

    def save_drift(self, experiment_id: str, file_path: str) -> str:
        artifact_path = "drift"
        return self._save_file(experiment_id=experiment_id, file_path=file_path, artifact_path=artifact_path)

    def save_model(self, experiment_id: str, obj: Any, file_path: str) -> str:
        artifact_path = "models"
        return self._save_artefact(
            experiment_id=experiment_id, obj=obj, file_path=file_path, artifact_path=artifact_path
        )

    # def download_model(self, model_uri: str) -> str:
    #     # 's3://mlflow/1/60aa90e454fe4ac09dd335573a50c0f9/artifacts/models/model.pkl'
    #     return self._download_artifact(artifact_uri=model_uri)
    #
    # def download_transformer(self, transformer_uri: str) -> str:
    #     # 's3://mlflow/1/60aa90e454fe4ac09dd335573a50c0f9/artifacts/transformer/input_transformer.pkl'
    #     return self._download_artifact(artifact_uri=transformer_uri)

    def download_artifact(self, artifact_uri: str) -> str:
        # 's3://mlflow/1/60aa90e454fe4ac09dd335573a50c0f9/artifacts/transformer/input_transformer.pkl'
        # 'file:///home/leo/flowi/mlruns/1/93f1eb92c95f4317ae1c1e3cd39f429a/artifacts/models/model.pkl'
        run_id = artifact_uri.split("/")[-4]
        path = "/".join(artifact_uri.split("/")[-2:])
        local_path = self._client.download_artifacts(run_id=run_id, path=path)

        return local_path
