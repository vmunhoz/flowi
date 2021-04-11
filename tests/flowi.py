from flowi.flow_chart.flow_chart import FlowChart
import os

FLOW_CHART = {
    "nodes": {
        "node-load-1": {
            "id": "node-load-1",
            "type": "Load",
            "properties": {
                "name": "LoadFile",
                "class": "LoadLocal",
                "attributes": {
                    "train_path": "iris.csv",
                    "test_path": '',
                    "test_split": 0.2,
                    "file_type": "csv"
                }
            }
        },
        "node-load-2": {
            "id": "node-load-2",
            "type": "Load",
            "properties": {
                "name": "LoadFile",
                "class": "LoadLocal",
                "attributes": {
                    "output_df": "train_df",
                    "train_path": "iris.csv",
                    "test_path": '',
                    "test_split": 0.2,
                    "file_type": "csv"
                }
            }
        },
        "node-fillna": {
            "id": "node-fillna",
            "type": "Preprocessing",
            "properties": {
                "name": "Fillna",
                "class": "Preprocessing",
                "attributes": {
                    "value": 0,
                    "method": None,
                    "axis": "index",
                    "merge_policy": "none"
                }
            }
        },
        "node-model-svc": {
            "id": "node-model-svc",
            "type": "Models",
            "properties": {
                "name": "svc",
                "class": "Classification",
                "attributes": {
                    "target_column": "class"
                }
            }
        },
        "node-metric-accuracy": {
            "id": "node-metric-accuracy",
            "type": "Metrics",
            "properties": {
                "name": "accuracy",
                "class": "Classification",
                "attributes": {
                    "target_column": "class"
                }
            }
        },
        "node-save": {
            "id": "node-save",
            "type": "Save",
            "properties": {
                "name": "SaveFile",
                "class": "SaveLocal",
                "attributes": {
                    "path": "saved.csv",
                    "file_type": "csv",
                    "merge_policy": "none"
                }
            }
        }
    },
    "links": {
        "link-load-fillna-1": {
            "from": {
                "nodeId": "node-load-1",
            },
            "to": {
                "nodeId": "node-fillna",
            },
        },
        "link-load-fillna-2": {
            "from": {
                "nodeId": "node-load-2",
            },
            "to": {
                "nodeId": "node-fillna",
            },
        },
        # "link-fillna-save": {
        #     "from": {
        #         "nodeId": "node-fillna",
        #     },
        #     "to": {
        #         "nodeId": "node-save",
        #     }
        # },
        "link-fillna-svc": {
            "from": {
                "nodeId": "node-fillna",
            },
            "to": {
                "nodeId": "node-model-svc",
            }
        },
        "link-svc-accuracy": {
            "from": {
                "nodeId": "node-model-svc",
            },
            "to": {
                "nodeId": "node-metric-accuracy",
            }
        },
        "link-accuracy-save": {
            "from": {
                "nodeId": "node-metric-accuracy",
            },
            "to": {
                "nodeId": "node-save",
            }
        }
    }
}


def test_end_to_end():
    flow_chart = FlowChart(flow_chart_json=FLOW_CHART)
    flow_chart.run()
    os.remove('saved.csv')
