import os
import warnings

# import librosa
# import numpy as np
# from PIL import Image
import dask.dataframe as dd

from flowi.components.component_base import ComponentBase

# warnings.filterwarnings('ignore')


class BaseLoader(ComponentBase):

    def load(self, file_type: str):
        return getattr(self, 'load_' + file_type)

    def load_csv(self, path: str):
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
