from typing import Any

from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger
import dask.dataframe as dd


class SaveLocal(ComponentBase):

    def __init__(self):
        super().__init__()
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        return dict()

    def save_file(self, df: dd.DataFrame, path: str, file_type: str) -> str:
        self._logger.debug('Loading files from directory: {}'.format(path))

        return self._save(file_type=file_type)(df, path)

    def _save(self, file_type: str):
        return getattr(self, '_save_' + file_type)

    @staticmethod
    def _save_csv(df: dd.DataFrame, path: str) -> str:
        df.to_csv(filename=path, single_file=True)

        return path
