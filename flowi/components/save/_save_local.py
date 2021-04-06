from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger
import dask.dataframe as dd


class SaveLocal(ComponentBase):

    def __init__(self):
        super().__init__()
        self._logger = Logger(logger_name=__name__)

    def save_file(self, input_variable_df: dd.DataFrame, path: str, file_type: str):
        self._logger.debug('Loading files from directory: {}'.format(path))

        return self._save(file_type=file_type)(input_variable_df, path)

    def _save(self, file_type: str):
        return getattr(self, '_save_' + file_type)

    @staticmethod
    def _save_csv(input_variable_df: dd.DataFrame, path: str):
        input_variable_df.to_csv(filename=path, single_file=True)
