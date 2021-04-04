from flowi.components.component_base import ComponentBase


def dummy_function(param1: str, param2: int):
    return param1, param2


def test_component_base():
    shared_variables = {
        'name': 'dummy_function',
    }