import json
import os

_XCOM_PATH = "/airflow/xcom/"


def _create_dir():
    os.makedirs(_XCOM_PATH, exist_ok=True)


def write_xcom(key: str, value: str):
    _create_dir()
    new_data = {key: value}

    xcom_file = os.path.join(_XCOM_PATH, "return.json")
    if not os.path.isfile(xcom_file):
        with open(xcom_file, mode="w") as f:
            f.write(json.dumps(new_data))
    else:
        with open(xcom_file) as f:
            xcom_data = json.load(f)

        xcom_data.update(new_data)
        with open(xcom_file, mode="w") as f:
            f.write(json.dumps(xcom_data))
