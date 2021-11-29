from typing import Any

import dask.dataframe as dd
from dask_ml.model_selection import RandomizedSearchCV
from scikeras.wrappers import KerasClassifier

from flowi.components.component_base import ComponentBase
from flowi.components.data_preparation import DataPreparationSKLearn
from flowi.components.models._wrappers import OneHotModel
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.utilities.logger import Logger


class ModelSelection(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        experiment_tracking = ExperimentTracking()
        model = result[0]
        parameters = result[1]

        experiment_tracking.save_model(obj=model, file_path="model")
        experiment_tracking.log_model_param(key=model.__class__.__name__, value=parameters)
        return {
            "model": model,
            "parameters": parameters,
            "target_column": methods_kwargs["target_column"],
            "object": model,
        }

    def random_search(
        self,
        df: dd.DataFrame,
        target_column: str,
        model,
        parameters: dict,
        early_stopping: bool or str = None,
        n_trials: int = 10,
        max_iter: int = 1,
        cv: int = 5,
        verbose: int = 0,
    ):
        if isinstance(model, OneHotModel):
            flowi_model = model
            model = flowi_model.model

            sklean_data_prep = DataPreparationSKLearn()
            X, y = sklean_data_prep.prepare_train(df=df, target_column=target_column)
            y = flowi_model.encode(y)
        else:
            sklean_data_prep = DataPreparationSKLearn()
            X, y = sklean_data_prep.prepare_train(df=df, target_column=target_column)
        tune_search = RandomizedSearchCV(
            estimator=model, param_distributions=parameters, n_jobs=-1, error_score=0, cv=cv
        )
        tune_search.fit(X, y)
        self._logger.debug(f"Model: {model.__class__.__name__}")
        self._logger.debug(f"Best Parameters: {tune_search.best_params_}")

        model = tune_search.best_estimator_
        if isinstance(model, KerasClassifier):
            flowi_model.model = model
            model = flowi_model

        return model, tune_search.best_params_
