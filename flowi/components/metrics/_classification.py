from typing import Any

import dask.dataframe as dd
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

    def accuracy(self, df: dd.DataFrame, test_df: dd.DataFrame, model, target_column: str):
        sklean_data_prep = DataPreparationSKLearn()
        X, y = sklean_data_prep.prepare_train(df=test_df, target_column=target_column)
        y_pred = model.predict(X)
        _, y_true = sklean_data_prep.prepare_train(df=df, target_column=target_column)

        accuracy = accuracy_score(y_true=y_true, y_pred=y_pred)
        print(accuracy)
        self._logger.debug(f'Accuracy: {accuracy}')

        return accuracy
