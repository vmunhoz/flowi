from typing import Any

import dask.dataframe as dd
import pandas as pd

from flowi.components.component_base import ComponentBase
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.utilities.logger import Logger

from dask_ml.impute import SimpleImputer
import numpy as np


class Preprocessing(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        del methods_kwargs["df"]

        experiment_tracking = ExperimentTracking()
        df = result[0]
        transformer = result[1]
        method_name = "_".join([method_name, str(id(transformer))])

        experiment_tracking.log_transformer_param(key=method_name, value=methods_kwargs)
        return {"df": df, "object": transformer, "transform_input": True}

    def fillna(
        self,
        df: dd.DataFrame,
        missing_values: int or float or str or np.nan or None = np.nan,
        strategy: str = "mean",
        fill_value: str or int or None = None,
    ):
        """
        Fill NA/NaN values using the specified method.
        docstring copied from dask documentation
        :param df: input dask Dataframe
        :param missing_values: The placeholder for the missing values. All occurrences of missing_values will be imputed. For pandas’ dataframes with nullable integer dtypes with missing values, missing_values should be set to np.nan, since pd.NA will be converted to np.nan.
        :param strategy: The imputation strategy. mean, median, most_frequent or constant
        :param fill_value: When strategy == “constant”, fill_value is used to replace all occurrences of missing_values. If left to the default, fill_value will be 0 when imputing numerical data and “missing_value” for strings or object data types.
        """
        self._logger.debug(f"missing_values: {missing_values}")
        self._logger.debug(f"strategy: {strategy}")

        transformer = SimpleImputer(missing_values=missing_values, strategy=strategy, fill_value=fill_value)
        transformer.fit(df)

        return transformer.transform(df), transformer
