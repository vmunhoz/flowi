from typing import Iterable

from sklearn.model_selection import ParameterGrid

from flowi.flow_chart.node import Node
from flowi.flow_chart.topology import Topology
from flowi.utilities.logger import Logger


class FlowChart(object):

    def __init__(self, flow_chart_json: dict):
        self._logger = Logger(logger_name=__name__)
        self._flow_chart_json = flow_chart_json
        self._runs_params = []
        self._parameter_tuning_types = ['Preprocessing']
        self._nodes_execution_order = []
        self._nodes = {}

        self._init_nodes()

    def _init_nodes(self):
        nodes = self._flow_chart_json['nodes']
        links = self._flow_chart_json['links']

        topology = Topology(nodes)
        for node_id in nodes:
            self._add_node(node=nodes[node_id])

        for link in links:
            node_from = links[link]['from']['nodeId']
            node_to = links[link]['to']['nodeId']
            topology.add_edge(node_from=node_from, node_to=node_to)

            self._add_node(node=nodes[node_from], next_node_id=node_to)
            self._add_node(node=nodes[node_to], previous_node_id=node_from)

        # for node_id in nodes:
        #     if node_id not in self._nodes:
        #         self._logger.warning(f'Node {node_id} is not linked to any node')
        #         self._add_node(node=nodes[node_id])

        self._nodes_execution_order = topology.topological_sort()
        self._logger.debug(f"Nodes running order: {self._nodes_execution_order}")
        self.generate_runs()

    def _add_node(self, node: dict, previous_node_id: str or None = None, next_node_id: str or None = None):
        node_id = node['id']
        previous_node = self._nodes.get(previous_node_id, None)
        next_node = self._nodes.get(next_node_id, None)

        if node_id not in self._nodes:
            self._nodes[node_id] = Node(id_=node_id, node=node, previous_node=previous_node, next_node=next_node)
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

    def run(self):
        for run_params in self._runs_params:
            global_variables = {}

            for node_id in self._nodes_execution_order:
                node: Node = self._nodes[node_id]
                self._logger.info(f'Processing node {node_id} | {node.type} - {node.method_name}')
                if node.type in self._parameter_tuning_types:
                    node.attributes = run_params[node_id]
                result = node.run(global_variables=global_variables)
