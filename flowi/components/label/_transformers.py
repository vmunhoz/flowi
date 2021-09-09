from dask_ml.preprocessing import OneHotEncoder, LabelEncoder

from sklearn.base import BaseEstimator, TransformerMixin


class OneHotEnc(BaseEstimator, TransformerMixin):
    def __init__(self, target_column: str):
        self._target_column = target_column
        self._transformer = OneHotEncoder()

    def get_categories(self):
        return self._transformer.categories_

    def fit(self, X, y=None):
        self._transformer.fit(X[self._target_column])
        return self

    def transform(self, X):
        X[self._target_column] = self._transformer.transform(X[self._target_column])
        return X


class LabelEnc(BaseEstimator, TransformerMixin):
    def __init__(self, target_column: str):
        self.target_column = target_column
        self._transformer = LabelEncoder()

    def get_classes(self):
        return self._transformer.classes_

    def fit(self, X, y=None):
        self._transformer.fit(X[self.target_column])
        return self

    def transform(self, X):
        X[self.target_column] = self._transformer.transform(X[self.target_column])
        return X

    def inverse_transform(self, X):
        return self._transformer.inverse_transform(X)
