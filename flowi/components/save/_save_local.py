from typing import Any

from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger
import dask.dataframe as dd


class SaveLocal(ComponentBase):
    def __init__(self):
        super().__init__()
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        return {"df": result}

    def save_file(
        self, df: dd.DataFrame, file_name: str, file_type: str, label_column: str, save_label_column_only: bool = True
    ) -> str:
        self._logger.debug("Saving file to directory: {}".format(file_name))
        if "flowi_label_class" in df.columns:
            df = df.rename(columns={"flowi_label_class": label_column})

        if save_label_column_only:
            self._save(file_type=file_type)(df[label_column], file_name)
        else:
            self._save(file_type=file_type)(df, file_name)

        return df

    def _save(self, file_type: str):
        return getattr(self, "_save_" + file_type)

    @staticmethod
    def _save_csv(df: dd.DataFrame, file_name: str) -> dd.DataFrame:
        df.to_csv(filename=file_name, single_file=True)

        return df
