import re


def convert_camel_to_snake(string: str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()
