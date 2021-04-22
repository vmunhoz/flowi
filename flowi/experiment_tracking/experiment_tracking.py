import os
from typing import Any

import mlflow

from flowi.experiment_tracking import Base
from flowi.utilities.logger import Logger
from flowi.utilities.singleton import Singleton
import flowi.experiment_tracking
from flowi import settings


class ExperimentTracking(Base, metaclass=Singleton):

    def __init__(self):
        self._logger = Logger(logger_name=__name__)
        self._experiment_tracking = self.get_experiment_tracking()

    @staticmethod
    def get_experiment_tracking():
        return getattr(flowi.experiment_tracking, settings.EXPERIMENT_TRACKING)(settings.FLOW_NAME)

    def start_run(self):
        self._experiment_tracking.start_run()

    def end_run(self):
        self._experiment_tracking.end_run()

    def set_param(self, key: str, value: str or int or float):
        self._experiment_tracking.set_param(key=key, value=value)

    @staticmethod
    def set_metric(metric_name: str, value: str or int or float):
        mlflow.log_metric(key=metric_name, value=value)

    def save_transformer(self, obj: Any, file_path: str) -> str:
        return self._experiment_tracking.save_transformer(obj=obj, file_path=file_path)

    def save_model(self, obj: Any, file_path: str) -> str:
        return self._experiment_tracking.save_model(obj=obj, file_path=file_path)
