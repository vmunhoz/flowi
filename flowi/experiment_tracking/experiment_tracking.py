import os
from typing import Any, List

import flowi.experiment_tracking
from flowi import settings
from flowi.experiment_tracking import Base
from flowi.utilities.logger import Logger
from flowi.utilities.singleton import Singleton


class ExperimentTracking(metaclass=Singleton):
    def __init__(self):
        self._logger: Logger = Logger(logger_name=__name__)
        self._experiment_tracking: Base = self._get_experiment_tracking()
        self._experiments_ids: List[str] = list()
        self._experiments_ids_copy: List[str] = list()
        self._current_experiment: str = ""

    def reset_experiments(self, num_experiments: int):
        self._experiments_ids = list()
        for i in range(num_experiments):
            experiment_id = self._experiment_tracking.start_experiment()
            self._experiments_ids.append(experiment_id)
        self._experiments_ids_copy = self._experiments_ids.copy()

    def get_experiment(self) -> str:
        return self._experiments_ids_copy.pop()

    def set_current_experiment(self, experiment_id: str):
        self._current_experiment = experiment_id

    @staticmethod
    def _get_experiment_tracking() -> Base:
        return getattr(flowi.experiment_tracking, settings.EXPERIMENT_TRACKING)(settings.FLOW_NAME, settings.VERSION)

    def end_experiments(self):
        for experiment_id in self._experiments_ids:
            self._experiment_tracking.end_experiment(experiment_id=experiment_id)

    def log_transformer_param(self, key: str, value: str or int or float):
        for experiment_id in self._experiments_ids:
            self._experiment_tracking.log_param(experiment_id=experiment_id, key=key, value=value)

    def log_model_param(self, key: str, value: str or int or float):
        self._experiment_tracking.log_param(experiment_id=self._current_experiment, key=key, value=value)

    def log_metric(self, metric_name: str, value: str or int or float):
        self._experiment_tracking.log_metric(experiment_id=self._current_experiment, key=metric_name, value=value)

    def save_transformer(self, obj: Any, file_path: str):
        return self._experiment_tracking.save_transformer(
            experiment_id=self._current_experiment, obj=obj, file_path=file_path
        )

    def save_columns(self, obj: Any, file_path: str):
        return self._experiment_tracking.save_columns(
            experiment_id=self._current_experiment, obj=obj, file_path=file_path
        )

    def save_drift(self, file_path: str) -> list:
        # from alibi_detect.utils.saving import save_detector
        # save_detector(obj, 'tmp_drift')
        # KSDrift.dill
        # meta.dill
        files = os.listdir(file_path)
        drift_detector_uris = []
        for file in files:
            new_file_path = os.path.join(file_path, file)
            uri = self._experiment_tracking.save_drift(experiment_id=self._current_experiment, file_path=new_file_path)
            drift_detector_uris.append(uri)

        return drift_detector_uris

    def save_model(self, obj: Any, file_path: str) -> str:
        return self._experiment_tracking.save_model(
            experiment_id=self._current_experiment, obj=obj, file_path=file_path
        )

    def download_artifact(self, artifact_uri: str):
        return self._experiment_tracking.download_artifact(artifact_uri=artifact_uri)
