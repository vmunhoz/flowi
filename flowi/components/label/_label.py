from typing import Any

import dask.dataframe as dd

from flowi.components.component_base import ComponentBase
from flowi.components.label._transformers import OneHotEnc, LabelEnc
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.utilities.logger import Logger


class Label(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        del methods_kwargs["df"]

        experiment_tracking = ExperimentTracking()
        df = result[0]
        transformer = result[1]
        method_name = "_".join([method_name, str(id(transformer))])
        transform_input = True if not methods_kwargs["is_label"] else False
        transform_output = True if methods_kwargs["is_label"] else False

        experiment_tracking.log_transformer_param(key=method_name, value=methods_kwargs)
        return {
            "df": df,
            "object": transformer,
            "transform_input": transform_input,
            "transform_output": transform_output,
        }

    def label_encoder(self, df: dd.DataFrame, target_column: str, is_label: bool):
        transformer = LabelEnc(target_column=target_column)
        transformer.fit(df)
        self._logger.debug(f"categories: {transformer.get_classes()}")
        df = transformer.transform(df)
        return df, transformer

    def one_hot_encoder(self, df: dd.DataFrame, target_column: str, is_label: bool):
        transformer = OneHotEnc(target_column=target_column)
        transformer.fit(df)
        self._logger.debug(f"categories: {transformer.get_categories()}")
        df = transformer.transform(df)
        return df, transformer
