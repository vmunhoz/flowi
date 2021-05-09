"""Run flowi flows
Usage:
------
    $ flowi --chart '{"nodes": {"node-load-1": {"id": "node-load-1", "type": "Load", "properties": {"name": "LoadFile", "class": "LoadLocal", "attributes": {"train_path": "tests/iris.csv", "test_path": "", "test_split": 0.2, "file_type": "csv"}}}, "node-load-2": {"id": "node-load-2", "type": "Load", "properties": {"name": "LoadFile", "class": "LoadLocal", "attributes": {"output_df": "train_df", "train_path": "tests/iris.csv", "test_path": "", "test_split": 0.2, "file_type": "csv"}}}, "node-fillna": {"id": "node-fillna", "type": "Preprocessing", "properties": {"name": "Fillna", "class": "Preprocessing", "attributes": {"strategy": ["mean", "median"]}}}, "node-label-enc": {"id": "node-label-enc", "type": "Label", "properties": {"name": "LabelEncoder", "class": "Label", "attributes": {"target_column": "class", "is_label": true}}}, "node-model-svc": {"id": "node-model-svc", "type": "Models", "properties": {"name": "svc", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-model-svc2": {"id": "node-model-svc2", "type": "Models", "properties": {"name": "svc", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-metric-accuracy": {"id": "node-metric-accuracy", "type": "Metrics", "properties": {"name": "accuracy", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-metric-accuracy2": {"id": "node-metric-accuracy2", "type": "Metrics", "properties": {"name": "accuracy", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-save": {"id": "node-save", "type": "Save", "properties": {"name": "SaveFile", "class": "SaveLocal", "attributes": {"path": "saved.csv", "file_type": "csv", "merge_policy": "none"}}}}, "links": {"link-load-fillna-1": {"from": {"nodeId": "node-load-1"}, "to": {"nodeId": "node-label-enc"}}, "link-load-fillna-2": {"from": {"nodeId": "node-load-2"}, "to": {"nodeId": "node-label-enc"}}, "link-label-enc-fillna": {"from": {"nodeId": "node-label-enc"}, "to": {"nodeId": "node-fillna"}}, "link-fillna-svc": {"from": {"nodeId": "node-fillna"}, "to": {"nodeId": "node-model-svc"}}, "link-fillna-svc2": {"from": {"nodeId": "node-fillna"}, "to": {"nodeId": "node-model-svc2"}}, "link-svc-accuracy": {"from": {"nodeId": "node-model-svc"}, "to": {"nodeId": "node-metric-accuracy"}}, "link-svc-accuracy2": {"from": {"nodeId": "node-model-svc2"}, "to": {"nodeId": "node-metric-accuracy2"}}, "link-accuracy-save": {"from": {"nodeId": "node-metric-accuracy"}, "to": {"nodeId": "node-save"}}, "link-accuracy2-save": {"from": {"nodeId": "node-metric-accuracy2"}, "to": {"nodeId": "node-save"}}}}'
"""

import argparse
import json

from flowi.flow_chart.flow_chart import FlowChart
from dask.distributed import Client

from flowi.settings import DASK_SCHEDULER

if __name__ == "__main__":
    train_parser = argparse.ArgumentParser(description="Training arguments")

    train_parser.add_argument("--chart", type=json.loads, help="flow chart")
    args = train_parser.parse_args()
    flow_chart_json = args.chart

    Client(address=DASK_SCHEDULER)
    flow_chart = FlowChart(flow_chart=flow_chart_json)
    flow_chart.run()
