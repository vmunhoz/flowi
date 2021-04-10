from typing import Any

import dask.dataframe as dd
import pandas as pd

from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger


class Preprocessing(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        return {
            'df': result
        }

    def fillna(self, df: dd.DataFrame, value: int or dict or pd.Series or dd.DataFrame,
               method: str = None, axis: str = 'index'):
        """
        Fill NA/NaN values using the specified method.
        docstring copied from dask documentation
        :param df: input dask Dataframe
        :param value: Value to use to fill holes (e.g. 0), alternately a dict/Series/DataFrame of values specifying which value to use for each index (for a Series) or column (for a DataFrame). Values not in the dict/Series/DataFrame will not be filled. This value cannot be a list.
        :param method: Method to use for filling holes in reindexed Series pad / ffill: propagate last valid observation forward to next valid backfill / bfill: use next valid observation to fill gap.
        :param axis: Axis along which to fill missing values.
        """
        self._logger.debug(f'value: {value}')
        self._logger.debug(f'value: {method}')
        return df.fillna(value=value, method=method, axis=axis)
