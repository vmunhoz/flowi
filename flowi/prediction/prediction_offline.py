import os
from flowi.flow_chart.node import Node
import dill
import dask.dataframe as dd


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
        X = input_transformer.transform(X)

    model = _load("model.pkl")
    y_pred = model.predict(X)

    output_transformer = _load("output_transformer.pkl")

    if output_transformer:
        y_pred = output_transformer.inverse_transform(X=y_pred)

    # save
    result_df = dd.from_array(y_pred, columns=["flowi_label_class"])
    source_node.state["df"] = source_result["test_df"].merge(result_df)
    destiny_node.run(global_variables={})
