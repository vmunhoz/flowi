from typing import Iterable

from sklearn.model_selection import ParameterGrid

from flowi.connections.aws.s3 import S3
from flowi.experiment_tracking.experiment_tracking import ExperimentTracking
from flowi.flow_chart.node import Node
from flowi.flow_chart.topology import Topology
from flowi.settings import FLOW_NAME, RUN_ID, VERSION
from flowi.utilities.logger import Logger
from flowi.utilities.mongo import Mongo


class FlowChart(object):
    def __init__(self, flow_chart: dict):
        self._logger = Logger(logger_name=__name__)
        self._mongo = Mongo()
        self._flow_chart = flow_chart
        self._experiment_tracking: ExperimentTracking = ExperimentTracking()
        self._runs_params = []
        self._parameter_tuning_types = ["Preprocessing"]
        self._nodes_execution_order = []
        self._nodes = {}
        self._num_experiments = 0

        self._init_nodes()

    def _init_nodes(self):
        nodes = self._flow_chart["nodes"]
        links = self._flow_chart["links"]

        topology = Topology(nodes)
        for node_id in nodes:
            self._add_node(node=nodes[node_id])

        for link in links:
            node_from = links[link]["from"]["nodeId"]
            node_to = links[link]["to"]["nodeId"]
            topology.add_edge(node_from=node_from, node_to=node_to)

            self._add_node(node=nodes[node_from], next_node_id=node_to)
            self._add_node(node=nodes[node_to], previous_node_id=node_from)

        self._nodes_execution_order = topology.topological_sort()
        self._logger.debug(f"Nodes running order: {self._nodes_execution_order}")
        self.generate_runs()

    def _add_node(self, node: dict, previous_node_id: str or None = None, next_node_id: str or None = None):
        node_id = node["id"]
        previous_node = self._nodes.get(previous_node_id, None)
        next_node = self._nodes.get(next_node_id, None)

        if node_id not in self._nodes:
            self._nodes[node_id] = Node(id_=node_id, node=node, previous_node=previous_node, next_node=next_node)
            if node["type"] == "Models":
                self._num_experiments += 1
        else:
            self._nodes[node_id].add_previous_node(previous_node=previous_node)
            self._nodes[node_id].add_next_node(next_node=next_node)

    def generate_runs(self):
        combined_grid_params = {}
        for node_id in self._nodes_execution_order:
            node: Node = self._nodes[node_id]
            if node.type not in self._parameter_tuning_types:
                continue

            for attribute in node.attributes:
                if isinstance(node.attributes[attribute], str) or not isinstance(node.attributes[attribute], Iterable):
                    node.attributes[attribute] = [node.attributes[attribute]]

            combined_grid_params[node_id] = list(ParameterGrid(node.attributes))
        combined_params = list(ParameterGrid(combined_grid_params))

        self._runs_params = combined_params

    def compare_models(self) -> dict:
        self._logger.info("Comparing models. Flow Name {} | RUN ID {} | Version {}".format(FLOW_NAME, RUN_ID, VERSION))
        models = self._mongo.get_models_by_version(flow_name=FLOW_NAME, run_id=RUN_ID, version=VERSION)
        best_model = None
        best_performance = 0.0
        for model in models:
            model_performance = model["metrics"]["accuracy"]
            if model_performance > best_performance:
                best_performance = model_performance
                best_model = model

        self._logger.info(best_model)

        return best_model

    def stage_model(self, model: dict):
        s3 = S3()
        run_id = model["run_id"]

        # model
        model_path = self._experiment_tracking.download_artifact(artifact_uri=model["model_uri"])
        s3.upload_artifact(local_path=model_path, run_id=run_id)

        columns_path = self._experiment_tracking.download_artifact(artifact_uri=model["columns_uri"])
        s3.upload_artifact(local_path=columns_path, run_id=run_id)

        drift_detector_uris = model["drift_detector_uri"]
        for drift_detector_uri in drift_detector_uris:
            drift_detector_path = self._experiment_tracking.download_artifact(artifact_uri=drift_detector_uri)
            s3.upload_artifact(local_path=drift_detector_path, run_id=run_id)

        input_transformer_path = self._experiment_tracking.download_artifact(
            artifact_uri=model["input_transformer_uri"]
        )
        s3.upload_artifact(local_path=input_transformer_path, run_id=run_id)

        output_transformer_path = self._experiment_tracking.download_artifact(
            artifact_uri=model["output_transformer_uri"]
        )
        s3.upload_artifact(local_path=output_transformer_path, run_id=run_id)

        self._mongo.stage_model(model["_id"])

    def run(self):
        for run_params in self._runs_params:
            global_variables = {}
            self._experiment_tracking.reset_experiments(num_experiments=self._num_experiments)

            for node_id in self._nodes_execution_order:
                node: Node = self._nodes[node_id]
                self._logger.info(f"Processing node {node_id} | {node.type} - {node.method_name}")
                if node.type in self._parameter_tuning_types:
                    node.attributes = run_params[node_id]
                node.run(global_variables=global_variables)

            self._experiment_tracking.end_experiments()

        best_model = self.compare_models()
        self.stage_model(model=best_model)
