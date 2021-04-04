from flowi.flow_chart.flow_chart import FlowChart
import os

FLOW_CHART = {
    "offset": {
        "x": 0,
        "y": 0
    },
    "nodes": {
        "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea34": {
            "id": "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea34",
            "position": {
                "x": 299,
                "y": 198.70001220703125
            },
            "orientation": 0,
            "type": "Load",
            "ports": {
                "port1": {
                    "id": "port1",
                    "type": "right",
                    "position": {
                        "x": 285,
                        "y": 42
                    }
                }
            },
            "properties": {
                "name": "LoadFile",
                "class": "LoadLocal",
                "description": "Loads data from path and returns the data and the file name",
                "output_policy": "create",
                "output_variables": [
                    "train_df"
                ],
                "input_variables": [

                ],
                "attributes": {
                    "output_df": "train_df",
                    "path": "test_dataset.csv",
                    "file_type": "csv"
                }
            },
            "size": {
                "width": 285,
                "height": 84
            }
        },
        "13e3b974-f59c-4e0c-b087-12eeb9cd068b": {
            "id": "13e3b974-f59c-4e0c-b087-12eeb9cd068b",
            "position": {
                "x": 780,
                "y": 201.70001220703125
            },
            "orientation": 0,
            "type": "Preprocessing",
            "ports": {
                "port1": {
                    "id": "port1",
                    "type": "left",
                    "position": {
                        "x": 0,
                        "y": 42
                    }
                },
                "port2": {
                    "id": "port2",
                    "type": "right",
                    "position": {
                        "x": 249,
                        "y": 42
                    }
                }
            },
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
            },
            "size": {
                "width": 249,
                "height": 84
            }
        },
        "14e3b974-f59c-4e0c-b087-12eeb9cd068b": {
            "id": "14e3b974-f59c-4e0c-b087-12eeb9cd068b",
            "position": {
                "x": 780,
                "y": 201.70001220703125
            },
            "orientation": 0,
            "type": "Save",
            "ports": {
                "port1": {
                    "id": "port1",
                    "type": "left",
                    "position": {
                        "x": 0,
                        "y": 42
                    }
                },
                "port2": {
                    "id": "port2",
                    "type": "right",
                    "position": {
                        "x": 249,
                        "y": 42
                    }
                }
            },
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
            },
            "size": {
                "width": 249,
                "height": 84
            }
        }
    },
    "links": {
        "86e6b84d-13ae-44cf-b11e-b374459d6d91": {
            "id": "86e6b84d-13ae-44cf-b11e-b374459d6d91",
            "from": {
                "nodeId": "2cb8f05f-9baf-4ce2-8a8e-fdaebeecea34",
                "portId": "port1"
            },
            "to": {
                "nodeId": "13e3b974-f59c-4e0c-b087-12eeb9cd068b",
                "portId": "port1"
            },
        },
        "96e6b84d-13ae-44cf-b11e-b374459d6d91": {
            "id": "86e6b84d-13ae-44cf-b11e-b374459d6d91",
            "from": {
                "nodeId": "13e3b974-f59c-4e0c-b087-12eeb9cd068b",
                "portId": "port1"
            },
            "to": {
                "nodeId": "14e3b974-f59c-4e0c-b087-12eeb9cd068b",
                "portId": "port1"
            },
        }
    },
    "selected": {
    },
    "hovered": {
    }
}


def test_end_to_end():
    print(type(FLOW_CHART))

    flow_chart = FlowChart(flow_chart_json=FLOW_CHART)
    flow_chart.run()
    os.remove('saved.csv')
