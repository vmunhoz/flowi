from typing import Any

from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger
import dask.dataframe as dd
from dask_ml.model_selection import train_test_split


class LoadLocal(ComponentBase):

    def __init__(self):
        super().__init__()
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        return {
            'df': result[0],
            'test_df': result[1]
        }

    def load_file(self, train_path: str, file_type: str = 'csv', test_path: str = '', test_split: float = 0.2) -> (dd.DataFrame, dd.DataFrame):
        self._logger.debug('Loading train file: {}'.format(train_path))
        train_df = self.load(file_type=file_type)(train_path)

        if test_path:
            test_df = self.load(file_type=file_type)(test_path)
        else:
            train_df, test_df = train_test_split(train_df, test_size=test_split, shuffle=False)

        return train_df, test_df

    def load(self, file_type: str):
        return getattr(self, '_load_' + file_type)

    @staticmethod
    def _load_csv(path: str):
        return dd.read_csv(path, blocksize="64MB")

    # @staticmethod
    # def load_audio(file_path: str) -> (np.ndarray, int):
    #     return librosa.load(file_path, sr=8000, mono=True)
    #
    # @staticmethod
    # def load_image(file_path: str) -> np.ndarray:
    #     pil_image = Image.open(file_path)
    #     np_image = np.asarray(pil_image)
    #     pil_image.close()
    #
    #     return np_image
    #
    # @staticmethod
    # def load_label_from_file_name(file_path: str):
    #     file_name = os.path.basename(file_path) if os.path.basename(file_path) else file_path
    #     extension_index = file_name.rfind('.')
    #     file_name = file_name[:extension_index]
    #
    #     return file_name
