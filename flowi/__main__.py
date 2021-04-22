"""Run flowi flows
Usage:
------
    $ flowi --chart {
    "nodes": {
        "node-load": {
            "id": "node-load",
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
        }
    },
    "links": {
        "link-load-svc": {
            "from": {
                "nodeId": "node-load",
            },
            "to": {
                "nodeId": "node-model-svc",
            },
        }
    }
"""

import argparse
import json

from flow_chart.flow_chart import FlowChart

if __name__ == '__main__':
    train_parser = argparse.ArgumentParser(description='Training arguments')

    train_parser.add_argument('--chart', type=json.loads, help='flow chart')
    args = train_parser.parse_args()
    flow_chart_json = args.chart

    flow_chart = FlowChart(flow_chart=flow_chart_json)
    flow_chart.run()
