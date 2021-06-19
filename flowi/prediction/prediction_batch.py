import os
from flowi.flow_chart.node import Node
import dill
import dask.dataframe as dd

from flowi.utilities.logger import Logger

_logger = Logger(logger_name=__name__)


def _load(file_path: str):
    if os.path.isfile(file_path):
        return dill.load(open(file_path, "rb"))

    return None


def predict(source: dict, destiny: dict, result_only: bool = True):
    source_node = Node(id_="source", node=source, previous_node=None, next_node=None)
    destiny_node = Node(id_="destiny", node=destiny, previous_node=source_node, next_node=None)

    source_result = source_node.run(global_variables={})
    X = source_result["test_df"]

    # transform
    input_transformer = _load("input_transformer.pkl")
    if input_transformer:
        _logger.info("Transforming input")
        X = input_transformer.transform(X)

    _logger.info("Predicting")
    model = _load("model.pkl")
    y_pred = model.predict(X)

    output_transformer = _load("output_transformer.pkl")
    if output_transformer:
        _logger.info("Transforming Output")
        y_pred = output_transformer.inverse_transform(X=y_pred)

    # save
    _logger.info("Saving results")
    result_df = dd.from_array(y_pred, columns=["flowi_label_class"])
    source_node.state["df"] = source_result["test_df"].merge(result_df)
    destiny_node.run(global_variables={})

    _logger.info("Finished Batch predict")
