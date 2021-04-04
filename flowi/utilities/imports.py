from importlib import import_module


def import_class(module_to_import: str):
    class_name = module_to_import.split('.')[-1]
    module_name = '.'.join(module_to_import.split('.')[:-1])

    module = import_module(module_name)
    return getattr(module, class_name)
