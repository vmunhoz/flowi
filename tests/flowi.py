from flowi.flow_chart.flow_chart import FlowChart
import os

FLOW_CHART = {
    "nodes": {
        "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea34": {
            "id": "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea34",
            "type": "Load",
            "properties": {
                "name": "LoadFile",
                "class": "LoadLocal",
                "output_policy": "create",
                "output_variables": [
                    "train_df"
                ],
                "input_variables": [

                ],
                "attributes": {
                    "output_df": "train_df",
                    "train_path": "test_dataset.csv",
                    "test_path": '',
                    "test_split": 0.2,
                    "file_type": "csv"
                }
            }
        },
        "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea35": {
            "id": "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea35",
            "type": "Load",
            "properties": {
                "name": "LoadFile",
                "class": "LoadLocal",
                "output_policy": "create",
                "output_variables": [
                    "train_df"
                ],
                "input_variables": [

                ],
                "attributes": {
                    "output_df": "train_df",
                    "train_path": "test_dataset2.csv",
                    "test_path": '',
                    "test_split": 0.2,
                    "file_type": "csv"
                }
            }
        },
        "13e3b974-f59c-4e0c-b087-12eeb9cd068b": {
            "id": "13e3b974-f59c-4e0c-b087-12eeb9cd068b",
            "type": "Preprocessing",
            "properties": {
                "name": "Fillna",
                "class": "Preprocessing",
                "description": "Compute a mel-scaled spectrogram.",
                "output_policy": "none",
                "output_variables": [
                    "train_df"
                ],
                "input_variables": [
                    "train_df"
                ],
                "attributes": {
                    "input_variable_df": "train_df",
                    "value": 0,
                    "method": None,
                    "axis": "index",
                    "merge_policy": "none"
                }
            }
        },
        "14e3b974-f59c-4e0c-b087-12eeb9cd068b": {
            "id": "14e3b974-f59c-4e0c-b087-12eeb9cd068b",
            "type": "Save",
            "properties": {
                "name": "SaveFile",
                "class": "SaveLocal",
                "description": "save local.",
                "output_policy": "none",
                "output_variables": [
                    "train_df"
                ],
                "input_variables": [
                    "train_df"
                ],
                "attributes": {
                    "input_variable_df": "train_df",
                    "path": "saved.csv",
                    "file_type": "csv",
                    "merge_policy": "none"
                }
            }
        }
    },
    "links": {
        "86e6b84d-13ae-44cf-b11e-b374459d6d91": {
            "id": "86e6b84d-13ae-44cf-b11e-b374459d6d91",
            "from": {
                "nodeId": "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea34",
            },
            "to": {
                "nodeId": "13e3b974-f59c-4e0c-b087-12eeb9cd068b",
            },
        },
        "86e6b84d-13ae-44cf-b11e-b374459d6d92": {
            "id": "86e6b84d-13ae-44cf-b11e-b374459d6d92",
            "from": {
                "nodeId": "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea35",
            },
            "to": {
                "nodeId": "13e3b974-f59c-4e0c-b087-12eeb9cd068b",
            },
        },
        "96e6b84d-13ae-44cf-b11e-b374459d6d91": {
            "id": "86e6b84d-13ae-44cf-b11e-b374459d6d91",
            "from": {
                "nodeId": "13e3b974-f59c-4e0c-b087-12eeb9cd068b",
            },
            "to": {
                "nodeId": "14e3b974-f59c-4e0c-b087-12eeb9cd068b",
            }
        }
    }
}


def test_end_to_end():
    flow_chart = FlowChart(flow_chart_json=FLOW_CHART)
    flow_chart.run()
    os.remove('saved.csv')
