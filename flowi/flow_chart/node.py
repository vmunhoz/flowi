from __future__ import annotations
from typing import Any, List

from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger
from flowi.utilities.imports import import_class
from flowi.utilities.strings import convert_camel_to_snake


class Node(object):

    def __init__(self, id_: str, node: dict, previous_node: str or None):
        self.id: str = id_
        node_type = node['type']
        self.method_name: str = convert_camel_to_snake(node['properties']['name'])
        self.type: str = node_type
        self.node_class = node['properties']['class']
        self.previous_nodes: List[Node] = [previous_node] if previous_node is not None else []
        self.changed_variables: list = []
        self.result: Any = None
        self.finished: bool = False
        self._logger = Logger(__name__)

        self.attributes: dict = node['properties']['attributes']
        self.output_policy: str = node['properties']['output_policy']

    def add_previous_node(self, previous_node: Node or None):
        if previous_node is not None:
            self.previous_nodes.append(previous_node)

    def _import_component(self):
        node_type = self.type.lower()
        snake_node_class = convert_camel_to_snake(self.node_class)

        return import_class(f'flowi.components.{node_type}.{self.node_class}')()

    def _mount_args(self, shared_variables: dict):
        args = {'method_name': self.method_name}

        for attribute in list(self.attributes.keys()):
            if attribute.startswith('input_variable_'):
                if attribute == 'input_variable_df':  # reserved key word
                    if len(self.previous_nodes) == 0:
                        raise IndexError('No previous node to get the dataframe from')
                    if len(self.previous_nodes) > 1:
                        raise IndexError('More than one previous node to get the dataframe from. Ambiguous operation.')
                    args[attribute] = self.previous_nodes[0].result
                else:
                    required_input = self.attributes[attribute]
                    args[attribute] = shared_variables[required_input]
                del self.attributes[attribute]

        return args

    def run(self, shared_variables: dict):
        component_class: ComponentBase = self._import_component()
        args = self._mount_args(shared_variables=shared_variables)
        result = component_class.apply(args, self.attributes)
        self._logger.debug(str(result))

        self.result = result
        self.finished = True

        return result
