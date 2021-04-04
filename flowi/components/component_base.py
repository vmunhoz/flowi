import inspect

from flowi.utilities.singleton import Singleton


class ComponentBase(metaclass=Singleton):

    def apply(self, shared_variables: dict, node_attributes: dict) -> dict:
        method_name = shared_variables['method_name']
        args = self._mount_args(shared_variables=shared_variables, alias=None,
                                node_attributes=node_attributes,
                                method_name=method_name)

        result = getattr(self, method_name)(**args)

        return result

    @staticmethod
    def _get_param_name(param_signature: str):
        if ':' in param_signature:
            return param_signature.split(':')[0]
        if '=' in param_signature:
            return param_signature.split('=')[0]

        return param_signature

    @staticmethod
    def _get_variable(node_attributes: dict, shared_variables: dict, param_name: str, alias: dict):
        param_name = param_name if param_name not in alias else alias[param_name]

        if param_name == 'node_attributes':
            return node_attributes

        if param_name in node_attributes:
            return node_attributes[param_name]

        return shared_variables[param_name]

    def _mount_args(self, node_attributes: dict, shared_variables: dict, alias: dict = None, method_name: str = ''):
        alias = alias if alias is not None else {}
        method_name = method_name if method_name else shared_variables['method_name']
        signature = inspect.signature(getattr(self, method_name))
        params = signature.parameters

        args = {}
        for param in params:
            param_sig = str(params[param])
            param_name = self._get_param_name(param_signature=param_sig)

            value = self._get_variable(node_attributes=node_attributes, shared_variables=shared_variables,
                                       param_name=param_name, alias=alias)

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
