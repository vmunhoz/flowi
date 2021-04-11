import inspect
from typing import Any

from flowi.utilities.singleton import Singleton


class ComponentBase(metaclass=Singleton):

    def apply(self, method_name: str, shared_variables: dict, node_attributes: dict) -> dict:
        kwargs = self._mount_args(method_name=method_name,
                                  shared_variables=shared_variables,
                                  node_attributes=node_attributes
                                  )

        result = getattr(self, method_name)(**kwargs)

        result = self._set_output(method_name=method_name, result=result, methods_kwargs=kwargs)
        if 'df' in kwargs:
            del kwargs['df']
        result['kwargs'] = kwargs
        return result

    def _set_output(self, method_name: str, result: Any, methods_kwargs: dict) -> dict:
        raise NotImplementedError('Component has to set a output policy')

    @staticmethod
    def _get_variable(param_name: str, default_value: Any, node_attributes: dict, shared_variables: dict):
        if param_name in node_attributes:
            return node_attributes[param_name]

        if param_name in shared_variables:
            return shared_variables[param_name]

        if isinstance(default_value, type(inspect.Signature.empty)):
            raise ValueError(f'Missing value for {param_name}')

        return default_value

    def _mount_args(self, method_name: str, node_attributes: dict, shared_variables: dict):
        signature = inspect.signature(getattr(self, method_name))
        params = signature.parameters

        args = {}
        for param in params:
            param_signature = params[param]
            param_name = param_signature.name
            default_value = param_signature.default

            value = self._get_variable(param_name=param_name,
                                       default_value=default_value,
                                       node_attributes=node_attributes,
                                       shared_variables=shared_variables
                                       )

            args[param_name] = value

        return args

    # @staticmethod
    # def _mount_output_variables(node_attributes: dict, result: dict):
    #     for attribute in node_attributes.keys():
    #         if attribute.startswith('output_'):
    #             output_variable_name = node_attributes[attribute]
    #             result[output_variable_name] = result.pop(attribute)
    #
    #     return result
