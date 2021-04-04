import types
from typing import Any

from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger


class PreprocessingBase(ComponentBase):
    def __init__(self, logger: Logger):
        self._logger = logger
    #
    # @staticmethod
    # def _append_response(preprocessed_data_list: list, response: Any):
    #     preprocessed_data_list = list(preprocessed_data_list)
    #
    #     if response is None:
    #         return preprocessed_data_list
    #
    #     if isinstance(response, types.GeneratorType):
    #         for generator_feature in response:
    #             preprocessed_data_list.append(generator_feature)
    #     else:
    #         preprocessed_data_list.append(response)
    #
    #     return preprocessed_data_list
