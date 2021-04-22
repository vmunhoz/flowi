from abc import abstractmethod
from typing import Any

import dill


class Base(object):

    @staticmethod
    def start_run():
        pass

    @staticmethod
    def end_run():
        pass

    @staticmethod
    def set_param(key: str, value: str or int or float):
        pass

    @staticmethod
    def set_metric(key: str, value: str or int or float):
        pass

    @staticmethod
    def _save_pickle(obj: Any, file_path: str) -> str:
        file_path = file_path if file_path.endswith('.pkl') else file_path + '.pkl'
        with open(file_path, 'wb') as f:
            dill.dump(obj=obj, file=f)

        return file_path

    @abstractmethod
    def save_transformer(self, obj: Any, file_path: str):
        pass

    @abstractmethod
    def save_model(self, obj: Any, file_path: str):
        pass
