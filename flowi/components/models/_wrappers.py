import dask.dataframe as dd
import dask.array as da
from dask_ml.preprocessing import DummyEncoder
from scikeras.wrappers import KerasClassifier
import numpy as np


class OneHotModel:
    def __init__(self, model: KerasClassifier):
        self.model = model
        self.encoder = DummyEncoder()

    def encode(self, y: dd.DataFrame or da.Array or np.ndarray) -> da.Array:
        if isinstance(y, np.ndarray):
            y = da.from_array(y)

        if isinstance(y, da.Array):
            y = y.to_dask_dataframe()

        y = y.astype("category")
        y = y.categorize()

        self.encoder.fit(y)
        y = self.encoder.transform(y)
        y = y.to_dask_array()

        return y

    def decode(self, y: dd.DataFrame or da.Array or np.ndarray) -> da.Array or np.ndarray:
        is_ndarray = False
        if isinstance(y, np.ndarray):
            y = da.from_array(y)
            is_ndarray = True

        y = self.encoder.inverse_transform(y)
        y = y.to_dask_array()
        if is_ndarray:
            y = y.compute()

        return y

    def predict(self, X) -> da.Array:
        y = self.model.predict(X)
        y = self.decode(y)
        return y
