from typing import Any

import numpy as np
from dask_ml.metrics import accuracy_score

from flowi.components.component_base import ComponentBase
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.utilities.logger import Logger


class Classification(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        experiment_tracking = ExperimentTracking()
        experiment_tracking.log_metric(metric_name=method_name, value=result)
        return {f"metric_{method_name}": result}

    def accuracy(self, y_pred: np.array, y_true: np.array, normalize: bool = True):
        accuracy = accuracy_score(y_true=y_true, y_pred=y_pred, normalize=normalize)
        self._logger.debug(f"Accuracy: {accuracy}")

        return accuracy
