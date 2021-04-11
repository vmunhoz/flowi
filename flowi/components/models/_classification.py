from pickle import dump
from typing import Any, List

import dask.dataframe as dd
from sklearn import svm

from flowi.components.component_base import ComponentBase
from flowi.components.model_selection import ModelSelection
from flowi.utilities.logger import Logger


class Classification(ComponentBase):
    def __init__(self):
        self._logger = Logger(logger_name=__name__)

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        pickle_name = 'model.pkl'
        dump(result[0], open(pickle_name, 'wb'))

        return {
            'model': result[0],
            'parameters': result[1],
            'target_column': methods_kwargs['target_column'],
            'pickle': pickle_name
        }

    @staticmethod
    def _fit_sklearn(df: dd.DataFrame, model, parameters: dict, target_column: str, verbose: int = 0,
                     has_model_selection_in_flow: bool = False):
        if not has_model_selection_in_flow:
            model_selection = ModelSelection()
            model, parameters = model_selection.random_search(df=df, model=model, parameters=parameters,
                                                              target_column=target_column, verbose=verbose)

        return model, parameters

    @staticmethod
    def _to_list(x: Any):
        return x if isinstance(x, list) else [x]

    def svc(self, df: dd.DataFrame, target_column: str,
            C: float or List[float] = 1.0, kernel: str or List[str] = 'rbf', degree: int or List[int] = 3,
            gamma: str or List[str] = 'scale', coef0: float or List[float] = 0.0,
            shrinking: bool or List[bool] = True, probability: bool or List[bool] = False,
            tol: float or List[float] = 1e-3, cache_size: float or List[float] = 200,
            class_weight: dict or str or List[str] or List[dict] = None, max_iter: int or List[int] = -1,
            decision_function_shape: str or List[str] = 'ovr', break_ties: bool or List[bool] = False,
            random_state: int or List[int] = None,
            verbose: int = 0,
            has_model_selection_in_next_step: bool = False):

        kernels = self._to_list(kernel)
        # Todo: Fix precomputed kernel
        # if 'precomputed' in kernels and X_train.shape[0] != X_train.shape[1]:
        if 'precomputed' in kernels:
            kernels.remove('precomputed')

        parameters = {
            'C': self._to_list(C),
            'kernel': kernels,
            'degree': self._to_list(degree),
            'gamma': self._to_list(gamma),
            'coef0': self._to_list(coef0),
            'shrinking': self._to_list(shrinking),
            'probability': self._to_list(probability),
            'tol': self._to_list(tol),
            'cache_size': self._to_list(cache_size),
            'class_weight': self._to_list(class_weight),
            'max_iter': self._to_list(max_iter),
            'decision_function_shape': self._to_list(decision_function_shape),
            'break_ties': self._to_list(break_ties),
            'random_state': self._to_list(random_state)
        }
        model = svm.SVC(**parameters)
        model, parameters = self._fit_sklearn(model=model,
                                              parameters=parameters,
                                              df=df,
                                              target_column=target_column,
                                              verbose=verbose,
                                              has_model_selection_in_flow=has_model_selection_in_next_step)

        return model, parameters
