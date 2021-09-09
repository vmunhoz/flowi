from typing import Any, List

import dask.dataframe as dd
from dask_ml.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin

from flowi.components.component_base import ComponentBase
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.utilities.logger import Logger

from dask_ml.impute import SimpleImputer
import numpy as np


class ColumnFilter(BaseEstimator, TransformerMixin):
    def __init__(self, columns: List[str], exclude_columns: List[str], transformer):
        self._columns = columns
        self._exclude_columns = exclude_columns
        self._transformer = transformer

        if self._columns and self._exclude_columns:
            raise ValueError("Columns and exclude_columns cannot be set together")

    def _filter_columns(self, X) -> List[str]:
        if self._columns:
            return self._columns
        elif self._exclude_columns:
            return X.columns.difference(self._exclude_columns).tolist()
        return X.columns.tolist()

    def fit(self, X):
        self._transformer.fit(X[self._filter_columns(X)])

    def transform(self, X):
        X[self._filter_columns(X)] = self._transformer.transform(X[self._filter_columns(X)])
        return X

    def inverse_transform(self, X):
        X[self._filter_columns(X)] = self._transformer.inverse_transform(X[self._filter_columns(X)])
        return X


class PreprocessingDataframe(ComponentBase):
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
        columns: List[str] = None,
        exclude_columns: List[str] = None,
        missing_values: int or float or str or np.nan or None = np.nan,
        strategy: str = "mean",
        fill_value: str or int or None = None,
    ):
        """
        Fill NA/NaN values using the specified method.
        docstring copied from dask documentation
        :param df: input dask Dataframe
        :param columns: columns to apply transform
        :param exclude_columns: columns excluded on apply transform
        :param missing_values: The placeholder for the missing values. All occurrences of missing_values will be imputed. For pandas’ dataframes with nullable integer dtypes with missing values, missing_values should be set to np.nan, since pd.NA will be converted to np.nan.
        :param strategy: The imputation strategy. mean, median, most_frequent or constant
        :param fill_value: When strategy == “constant”, fill_value is used to replace all occurrences of missing_values. If left to the default, fill_value will be 0 when imputing numerical data and “missing_value” for strings or object data types.
        """
        self._logger.debug(f"missing_values: {missing_values}")
        self._logger.debug(f"strategy: {strategy}")

        base_transformer = SimpleImputer(missing_values=missing_values, strategy=strategy, fill_value=fill_value)
        transformer = ColumnFilter(columns=columns, exclude_columns=exclude_columns, transformer=base_transformer)
        transformer.fit(df)

        return transformer.transform(df), transformer

    def standard_scaler(
        self,
        df: dd.DataFrame,
        columns: List[str] = None,
        exclude_columns: List[str] = None,
        with_mean: bool = True,
        with_std: bool = True,
    ):
        """
        Standardize features by removing the mean and scaling to unit variance
        :param df: input dask Dataframe
        :param columns: columns to apply transform
        :param exclude_columns: columns excluded on apply transform
        :param with_mean: If True, center the data before scaling. This does not work (and will raise an exception) when attempted on sparse matrices, because centering them entails building a dense matrix which in common use cases is likely to be too large to fit in memory.
        :param with_std: If True, scale the data to unit variance (or equivalently, unit standard deviation).
        """
        self._logger.debug(f"with_mean: {with_mean}")
        self._logger.debug(f"with_std: {with_std}")

        base_transformer = StandardScaler(with_mean=with_mean, with_std=with_std)
        transformer = ColumnFilter(columns=columns, exclude_columns=exclude_columns, transformer=base_transformer)
        transformer.fit(df)

        return transformer.transform(df), transformer
