from typing import Any

import numpy as np
import dask.dataframe as dd

from flowi.components.component_base import ComponentBase
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.utilities.logger import Logger

from alibi_detect.cd import KSDrift


class Drift(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        experiment_tracking = ExperimentTracking()

        drift_detector_uri = experiment_tracking.save_drift(obj=result, file_path="drift_detector")
        return {"df": methods_kwargs["df"], "object": result, "drift_detector_uri": drift_detector_uri}

    @staticmethod
    def _handle_df(df: dd.DataFrame):
        n_samples = 400
        length = len(df)
        fraction = min(n_samples / length, 1)
        df = df.sample(frac=fraction)
        df = df.values.compute()

        return df

    def kolmogorov_smirnov(self, df: dd.DataFrame or np.array):
        p_val = 0.05

        if isinstance(df, dd.DataFrame):
            df = self._handle_df(df)

        drift_detector = KSDrift(df, p_val=p_val)

        return drift_detector
