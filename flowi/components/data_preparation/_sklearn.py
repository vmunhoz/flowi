from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger
import dask.dataframe as dd
import dask.array as da


class DataPreparationSKLearn(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    @staticmethod
    def prepare_train(df: dd.DataFrame, target_column: str) -> (da.Array, da.Array):
        data_columns = list(df.columns)
        data_columns.remove(target_column)

        X_df = df[data_columns]
        y_df = df[[target_column]]
        X = X_df.to_dask_array()
        y = y_df.to_dask_array()

        return X, y
