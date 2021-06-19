"""Run flowi flows
Usage:
------
    $ flowi train --chart '{"nodes": {"node-load-1": {"id": "node-load-1", "type": "Load", "properties": {"name": "LoadFile", "class": "LoadLocal", "attributes": {"train_path": "tests/iris.csv", "test_path": "", "test_split": 0.2, "file_type": "csv"}}}, "node-load-2": {"id": "node-load-2", "type": "Load", "properties": {"name": "LoadFile", "class": "LoadLocal", "attributes": {"output_df": "train_df", "train_path": "tests/iris.csv", "test_path": "", "test_split": 0.2, "file_type": "csv"}}}, "node-fillna": {"id": "node-fillna", "type": "Preprocessing", "properties": {"name": "Fillna", "class": "Preprocessing", "attributes": {"strategy": ["mean", "median"]}}}, "node-label-enc": {"id": "node-label-enc", "type": "Label", "properties": {"name": "LabelEncoder", "class": "Label", "attributes": {"target_column": "class", "is_label": true}}}, "node-model-svc": {"id": "node-model-svc", "type": "Models", "properties": {"name": "svc", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-model-svc2": {"id": "node-model-svc2", "type": "Models", "properties": {"name": "svc", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-metric-accuracy": {"id": "node-metric-accuracy", "type": "Metrics", "properties": {"name": "accuracy", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-metric-accuracy2": {"id": "node-metric-accuracy2", "type": "Metrics", "properties": {"name": "accuracy", "class": "Classification", "attributes": {"target_column": "class"}}}, "node-save": {"id": "node-save", "type": "Save", "properties": {"name": "SaveFile", "class": "SaveLocal", "attributes": {"path": "saved.csv", "file_type": "csv", "merge_policy": "none"}}}}, "links": {"link-load-fillna-1": {"from": {"nodeId": "node-load-1"}, "to": {"nodeId": "node-label-enc"}}, "link-load-fillna-2": {"from": {"nodeId": "node-load-2"}, "to": {"nodeId": "node-label-enc"}}, "link-label-enc-fillna": {"from": {"nodeId": "node-label-enc"}, "to": {"nodeId": "node-fillna"}}, "link-fillna-svc": {"from": {"nodeId": "node-fillna"}, "to": {"nodeId": "node-model-svc"}}, "link-fillna-svc2": {"from": {"nodeId": "node-fillna"}, "to": {"nodeId": "node-model-svc2"}}, "link-svc-accuracy": {"from": {"nodeId": "node-model-svc"}, "to": {"nodeId": "node-metric-accuracy"}}, "link-svc-accuracy2": {"from": {"nodeId": "node-model-svc2"}, "to": {"nodeId": "node-metric-accuracy2"}}, "link-accuracy-save": {"from": {"nodeId": "node-metric-accuracy"}, "to": {"nodeId": "node-save"}}, "link-accuracy2-save": {"from": {"nodeId": "node-metric-accuracy2"}, "to": {"nodeId": "node-save"}}}}'
"""

import argparse
import ast
import json
import sys

from dask.distributed import Client

from flowi.flow_chart.flow_chart import FlowChart
from flowi.prediction import prediction_batch
from flowi.settings import DASK_SCHEDULER


def _json_load(string: str) -> dict:
    loaded_json = None
    if isinstance(string, str):
        try:
            loaded_json = json.loads(string)
        except json.decoder.JSONDecodeError:
            loaded_json = ast.literal_eval(string)
    return loaded_json


def train(args):
    flow_chart_json = _json_load(args.chart)

    flow_chart = FlowChart(flow_chart=flow_chart_json)
    flow_chart.run()


def predict(args):
    source = _json_load(args.source)
    destiny = _json_load(args.destiny)
    prediction_batch.predict(source=source, destiny=destiny)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    flowi_parser = argparse.ArgumentParser(description="Flowi CLI")
    subparsers = flowi_parser.add_subparsers(dest="command", help="sub-command help", required=True)

    train_parser = subparsers.add_parser("train", help="train help")
    train_parser.add_argument("--chart", type=str, help="flow chart", required=True)

    predict_parser = subparsers.add_parser("predict", help="predict help")
    predict_parser.add_argument("--source", type=str, help="Prediction data source", required=True)
    predict_parser.add_argument("--destiny", type=str, help="Where to dump predictions", required=True)

    args = flowi_parser.parse_args(args)
    Client(address=DASK_SCHEDULER)
    if args.command == "train":
        train(args=args)
    elif args.command == "predict":
        predict(args=args)
    else:
        raise NameError("Command name error")


if __name__ == "__main__":
    main()
