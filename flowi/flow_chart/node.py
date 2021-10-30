from __future__ import annotations

from typing import List

from flowi.components.component_base import ComponentBase
from flowi.components.monitoring import Drift
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.prediction.prediction_flow import create_transform_pipeline
from flowi.utilities.imports import import_class
from flowi.utilities.logger import Logger
from flowi.utilities.mongo import Mongo
from flowi.utilities.strings import convert_camel_to_snake


class Node(object):
    def __init__(self, id_: str, node: dict, previous_node: str or None, next_node: str or None):
        self.id: str = id_
        node_type = node["type"]
        self.method_name: str = convert_camel_to_snake(node["properties"]["name"])
        self.type: str = node_type
        self.node_class = node["properties"]["class"]
        self.previous_nodes: List[Node] = [previous_node] if previous_node is not None else []
        self.next_nodes: List[Node] = [next_node] if next_node is not None else []
        self.changed_variables: list = []
        self.state: dict = dict()
        self.prediction_flow: List[dict] = []
        self.finished: bool = False
        self._logger = Logger(__name__)
        self._experiment_tracking: ExperimentTracking = ExperimentTracking()
        self._mongo = Mongo()

        self.attributes: dict = node["properties"]["attributes"]

    def add_previous_node(self, previous_node: Node or None):
        if previous_node is not None:
            self.previous_nodes.append(previous_node)

    def add_next_node(self, next_node: Node or None):
        if next_node is not None:
            self.next_nodes.append(next_node)

    def _get_class_name(self):
        node_type = self.type.lower()
        return f"flowi.components.{node_type}.{self.node_class}"

    def _import_component(self):
        class_name = self._get_class_name()

        return import_class(class_name)()

    def _prepare_state(self):
        state = {
            "df": self._append_incoming_df(attribute_type="df"),
            "test_df": self._append_incoming_df(attribute_type="test_df"),
            "model": self._get_incoming_attribute("model"),
            "model_uri": self._get_incoming_attribute("model_uri"),
            "parameters": self._get_incoming_attribute("parameters"),
            "y_pred": self._get_incoming_attribute("y_pred"),
            "y_true": self._get_incoming_attribute("y_true"),
            "has_model_selection_in_next_step": self._model_selection_in_next(),
            "experiment_id": self._get_incoming_attribute("experiment_id"),
            "mongo_id": self._get_incoming_attribute("mongo_id"),
        }

        return state

    def set_current_experiment(self):
        if self.type == "Models" or self.type == "ModelSelection":
            experiment_id = self._experiment_tracking.get_experiment()
            self.state["experiment_id"] = experiment_id
        else:
            experiment_id = self.state["experiment_id"]

        self._experiment_tracking.set_current_experiment(experiment_id)

    def _model_selection_in_next(self):
        for next_node in self.next_nodes:
            if next_node.type == "ModelSelection":
                return True
        return False

    def _append_incoming_df(self, attribute_type: str):
        """
        Append (concatenate) incoming dataframes from previous nodes.
        :param attribute_type: train_df or test_df
        :return: appended (concatenated) dataframe
        """
        if len(self.previous_nodes) > 0:
            concat_df = self.previous_nodes[0].state[attribute_type]
            for i in range(1, len(self.previous_nodes)):
                concat_df = concat_df.append(self.previous_nodes[i].state[attribute_type])
            return concat_df
        else:
            return None

    def _get_incoming_attribute(self, attribute_name: str):
        if len(self.previous_nodes) > 0:
            for previous_node in self.previous_nodes:
                attribute = previous_node.state[attribute_name]
                return attribute

        return None

    def _get_incoming_prediction_flow(self):
        prediction_flow = []
        ids = []
        if len(self.previous_nodes) > 0:
            for previous_node in self.previous_nodes:
                current_prediction_flow = previous_node.prediction_flow
                for step in current_prediction_flow:
                    if step["id"] not in ids:
                        ids.append(step["id"])
                        prediction_flow.append(step)

        return prediction_flow

    def _update_prediction_flow(self, result: dict):
        self.prediction_flow = self._get_incoming_prediction_flow()
        class_name = self._get_class_name()

        if not (
            self.type in ["Load", "Metrics"]
            or (self.type == "Model" and not self.state["has_model_selection_in_next_step"])
        ):
            step = {
                "id": self.id,
                "class_name": class_name,
                "method_name": self.method_name,
                "object": result.get("object"),
                "transform_input": result.get("transform_input"),
                "transform_output": result.get("transform_output"),
            }
            self.prediction_flow.append(step)

    def _drift_detection(self):
        drift = Drift()
        x_df = self.state["df"]
        x_df = x_df.drop(columns=[self.state["target_column"]])

        drift_return = drift.apply(method_name="kolmogorov_smirnov", shared_variables={}, node_attributes={"df": x_df})
        return drift_return["drift_detector_uri"]
        # self._mongo.add_drift(mongo_id=self.state["mongo_id"], drift_name="kolmogorov_smirnov")

    def predict_if_necessary(self):
        class_name = self._get_class_name()
        if "model_selection" in class_name or (
            "model" in class_name and not self.state["has_model_selection_in_next_step"]
        ):

            df = self.state["test_df"]
            y_true = df[self.state["target_column"]].values.compute()

            df = df.drop(columns=[self.state["target_column"]])
            columns = df.columns.tolist()
            columns_uri = self._experiment_tracking.save_columns(obj=columns, file_path="columns")
            X = df

            input_transformer = create_transform_pipeline(
                prediction_flow=self.prediction_flow, transform_type="transform_input"
            )
            input_transformer_uri = ""
            if input_transformer is not None:
                input_transformer_uri = self._experiment_tracking.save_transformer(
                    obj=input_transformer, file_path="input_transformer"
                )
                X = input_transformer.transform(X=df)

            y_pred = self.state["model"].predict(X=X)

            output_transformer = create_transform_pipeline(
                prediction_flow=self.prediction_flow, transform_type="transform_output"
            )
            output_transformer_uri = ""
            if output_transformer is not None:
                output_transformer_uri = self._experiment_tracking.save_transformer(
                    obj=output_transformer, file_path="output_transformer"
                )
                y_pred = output_transformer.inverse_transform(X=y_pred)

            self.state["y_pred"] = y_pred
            self.state["y_true"] = y_true

            drift_detector_uri = self._drift_detection()

            self.state["mongo_id"] = self._mongo.insert(
                experiment_id=self.state["experiment_id"],
                model_uri=self.state["model_uri"],
                columns_uri=columns_uri,
                drift_detector_uri=drift_detector_uri,
                input_transformer_uri=input_transformer_uri,
                output_transformer_uri=output_transformer_uri,
            )

    def _pre_run(self):
        self.state = self._prepare_state()
        self.set_current_experiment()

    def run(self, global_variables: dict):
        component_class: ComponentBase = self._import_component()
        self._pre_run()

        result = component_class.apply(self.method_name, self.state, self.attributes)

        self.state.update(result)
        self._update_prediction_flow(result=result)

        self.post_run()
        self.finished = True

        return result

    def post_run(self):
        self.predict_if_necessary()
        if self.type == "Metrics":
            value = self.state[f"metric_{self.method_name}"]
            self._mongo.add_metric(mongo_id=self.state["mongo_id"], metric_name=self.method_name, value=value)
