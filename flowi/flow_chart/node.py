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
        self.result: dict = dict()
        self.finished: bool = False
        self._logger = Logger(__name__)

        self.attributes: dict = node['properties']['attributes']
        self.output_policy: str = node['properties']['output_policy']

    def add_previous_node(self, previous_node: Node or None):
        if previous_node is not None:
            self.previous_nodes.append(previous_node)

    def _import_component(self):
        node_type = self.type.lower()

        return import_class(f'flowi.components.{node_type}.{self.node_class}')()

    def prepare_attributes(self):
        prepared_attributes = {
            'train_df': self._append_incoming(attribute_type='train_df'),
            'test_df': self._append_incoming(attribute_type='test_df')
        }
        return prepared_attributes

    def _append_incoming(self, attribute_type: str):
        """
        Append (concatenate) incoming dataframes from previous nodes.
        :param attribute_type: train_df or test_df
        :return: appended (concatenated) dataframe
        """
        if len(self.previous_nodes) > 0:
            concat_df = self.previous_nodes[0].result[attribute_type]
            for i in range(1, len(self.previous_nodes)):
                concat_df = concat_df.append(self.previous_nodes[i].result[attribute_type])
            return concat_df
        else:
            return None

    def _mount_args(self, shared_variables: dict, prepared_attributes: dict):
        args = {'method_name': self.method_name}

        for attribute in list(self.attributes.keys()):
            if attribute.startswith('input_variable_'):
                if attribute == 'input_variable_df':  # reserved key word
                    if len(self.previous_nodes) == 0:
                        raise IndexError('No previous node to get the dataframe from')
                    args[attribute] = prepared_attributes['train_df']
                else:
                    required_input = self.attributes[attribute]
                    args[attribute] = shared_variables[required_input]
                del self.attributes[attribute]

        return args

    def update_result(self, result: Any, prepared_attributes: dict):
        if type(result) == dict:
            self.result = result
        else:
            self.result['train_df'] = result

        for key in prepared_attributes.keys():
            if key not in self.result.keys():
                self.result[key] = prepared_attributes[key]

    def run(self, shared_variables: dict):
        component_class: ComponentBase = self._import_component()

        prepared_attributes = self.prepare_attributes()
        args = self._mount_args(shared_variables=shared_variables, prepared_attributes=prepared_attributes)
        result = component_class.apply(args, self.attributes)
        self._logger.debug(str(result))

        self.update_result(result=result, prepared_attributes=prepared_attributes)
        self.finished = True

        return result
