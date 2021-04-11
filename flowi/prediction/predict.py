from typing import List
from pickle import load
import numpy as np

from flowi.utilities.imports import import_class
import dask.dataframe as dd


def predict(x: dd.DataFrame or np.array, prediction_flow: List[dict]):
    if not isinstance(x, dd.DataFrame):
        df = dd.from_array(x=x)
    else:
        df = x

    for step in prediction_flow:
        component_class = import_class(step['class_name'])()
        if step['pickle'] is None:
            kwargs = step['kwargs']
            result = component_class.apply(method_name=step['method_name'], shared_variables={'df': df}, node_attributes=kwargs)
            df = result['df']
        else:
            transformer = load(open(step['pickle'], 'rb'))
            if 'model' not in step['class_name']:
                df = transformer.transform()
            else:
                return transformer.predict(df.values)

    raise BrokenPipeError('Missing model to predict')
