from typing import Any

import dask.dataframe as dd
import numpy as np
from dask_ml.metrics import accuracy_score

from flowi.components.component_base import ComponentBase
from flowi.components.data_preparation import DataPreparationSKLearn
from flowi.utilities.logger import Logger


class Classification(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        return {
            f'metric_{method_name}': result
        }

    def accuracy(self, y_pred: np.array, y_true: np.array):
        accuracy = accuracy_score(y_true=y_true, y_pred=y_pred)
        self._logger.debug(f'Accuracy: {accuracy}')

        return accuracy
