from __future__ import annotations
from typing import Any, List

from flowi.components.component_base import ComponentBase
from flowi.utilities.logger import Logger
from flowi.utilities.imports import import_class
from flowi.utilities.strings import convert_camel_to_snake
from flowi.prediction.predict import predict


class Node(object):

    def __init__(self, id_: str, node: dict, previous_node: str or None, next_node: str or None):
        self.id: str = id_
        node_type = node['type']
        self.method_name: str = convert_camel_to_snake(node['properties']['name'])
        self.type: str = node_type
        self.node_class = node['properties']['class']
        self.previous_nodes: List[Node] = [previous_node] if previous_node is not None else []
        self.next_nodes: List[Node] = [next_node] if next_node is not None else []
        self.changed_variables: list = []
        self.state: dict = dict()
        self.prediction_flow: List[dict] = []
        self.finished: bool = False
        self._logger = Logger(__name__)

        self.attributes: dict = node['properties']['attributes']

    def add_previous_node(self, previous_node: Node or None):
        if previous_node is not None:
            self.previous_nodes.append(previous_node)

    def add_next_node(self, next_node: Node or None):
        if next_node is not None:
            self.next_nodes.append(next_node)

    def _get_class_name(self):
        node_type = self.type.lower()
        return f'flowi.components.{node_type}.{self.node_class}'

    def _import_component(self):
        class_name = self._get_class_name()

        return import_class(class_name)()

    def _prepare_state(self):
        state = {
            'df': self._append_incoming_df(attribute_type='df'),
            'test_df': self._append_incoming_df(attribute_type='test_df'),
            'model': self._get_incoming_attribute('model'),
            'parameters': self._get_incoming_attribute('parameters'),
            'y_pred': self._get_incoming_attribute('y_pred'),
            'y_true': self._get_incoming_attribute('y_true'),
            'has_model_selection_in_next_step': self._model_selection_in_next()
        }
        return state

    def _model_selection_in_next(self):
        for next_node in self.next_nodes:
            if next_node.type == 'ModelSelection':
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

    def _update_result(self, result: Any, prepared_attributes: dict):
        if type(result) == dict:
            self.state = result
        else:
            self.state['train_df'] = result

        for key in prepared_attributes.keys():
            if key not in self.state.keys():
                self.state[key] = prepared_attributes[key]

    def _get_incoming_prediction_flow(self):
        prediction_flow = []
        ids = []
        if len(self.previous_nodes) > 0:
            for previous_node in self.previous_nodes:
                current_prediction_flow = previous_node.prediction_flow
                for step in current_prediction_flow:
                    if step['id'] not in ids:
                        ids.append(step['id'])
                        prediction_flow.append(step)

        return prediction_flow

    def _update_prediction_flow(self, result: dict):
        self.prediction_flow = self._get_incoming_prediction_flow()
        class_name = self._get_class_name()

        if 'preprocessing' in class_name or 'model_selection' in class_name \
                or ('model' in class_name and not self.state['has_model_selection_in_next_step']):
            step = {
                'id': self.id,
                'class_name': class_name,
                'method_name': self.method_name,
                'kwargs': result.get('kwargs'),
                'pickle': result.get('pickle'),
            }
            self.prediction_flow.append(step)

    def run(self, global_variables: dict):
        component_class: ComponentBase = self._import_component()

        self.state = self._prepare_state()

        result = component_class.apply(self.method_name, self.state, self.attributes)
        self._logger.debug(str(result))

        self.state.update(result)
        self._update_prediction_flow(result=result)

        class_name = self._get_class_name()
        if 'model_selection' in class_name \
                or ('model' in class_name and not self.state['has_model_selection_in_next_step']):
            df = self.state['test_df']
            self.state['y_true'] = df[self.state['target_column']].values.compute()

            df = df.drop(columns=[self.state['target_column']])
            self.state['y_pred'] = predict(x=df, prediction_flow=self.prediction_flow)

        self.finished = True

        return result
