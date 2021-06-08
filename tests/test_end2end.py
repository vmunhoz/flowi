import json
import os
from unittest import mock

import pymongo

import flowi.settings
from flowi.__main__ import main

FLOW_CHART = {
    "nodes": {
        "node-load-1": {
            "id": "node-load-1",
            "type": "Load",
            "properties": {
                "name": "LoadFile",
                "class": "LoadLocal",
                "attributes": {"train_path": "iris.csv", "test_path": "", "test_split": 0.2, "file_type": "csv"},
            },
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
                    "test_path": "",
                    "test_split": 0.2,
                    "file_type": "csv",
                },
            },
        },
        "node-fillna": {
            "id": "node-fillna",
            "type": "Preprocessing",
            "properties": {"name": "Fillna", "class": "Preprocessing", "attributes": {"strategy": ["mean", "median"]}},
        },
        "node-label-enc": {
            "id": "node-label-enc",
            "type": "Label",
            "properties": {
                "name": "LabelEncoder",
                "class": "Label",
                "attributes": {"target_column": "class", "is_label": True},
            },
        },
        "node-model-svc": {
            "id": "node-model-svc",
            "type": "Models",
            "properties": {"name": "svc", "class": "Classification", "attributes": {"target_column": "class"}},
        },
        "node-model-svc2": {
            "id": "node-model-svc2",
            "type": "Models",
            "properties": {"name": "svc", "class": "Classification", "attributes": {"target_column": "class"}},
        },
        "node-metric-accuracy": {
            "id": "node-metric-accuracy",
            "type": "Metrics",
            "properties": {"name": "accuracy", "class": "Classification", "attributes": {"target_column": "class"}},
        },
        "node-metric-accuracy2": {
            "id": "node-metric-accuracy2",
            "type": "Metrics",
            "properties": {"name": "accuracy", "class": "Classification", "attributes": {"target_column": "class"}},
        },
        "node-save": {
            "id": "node-save",
            "type": "Save",
            "properties": {
                "name": "SaveFile",
                "class": "SaveLocal",
                "attributes": {"file_type": "csv", "file_name": "saved.csv", "label_column": "class"},
            },
        },
    },
    "links": {
        "link-load-fillna-1": {"from": {"nodeId": "node-load-1"}, "to": {"nodeId": "node-label-enc"}},
        "link-load-fillna-2": {"from": {"nodeId": "node-load-2"}, "to": {"nodeId": "node-label-enc"}},
        "link-label-enc-fillna": {"from": {"nodeId": "node-label-enc"}, "to": {"nodeId": "node-fillna"}},
        "link-fillna-svc": {"from": {"nodeId": "node-fillna"}, "to": {"nodeId": "node-model-svc"}},
        "link-fillna-svc2": {"from": {"nodeId": "node-fillna"}, "to": {"nodeId": "node-model-svc2"}},
        "link-svc-accuracy": {"from": {"nodeId": "node-model-svc"}, "to": {"nodeId": "node-metric-accuracy"}},
        "link-svc-accuracy2": {"from": {"nodeId": "node-model-svc2"}, "to": {"nodeId": "node-metric-accuracy2"}},
        "link-accuracy-save": {"from": {"nodeId": "node-metric-accuracy"}, "to": {"nodeId": "node-save"}},
        "link-accuracy2-save": {"from": {"nodeId": "node-metric-accuracy2"}, "to": {"nodeId": "node-save"}},
    },
}


def test_end_to_end_train(mocker):
    mocker.patch.object(flowi.settings, "FLOW_NAME", "End2End Test Flow")
    mocker.patch.object(flowi.settings, "EXPERIMENT_TRACKING", "MLflow")
    with mock.patch("flowi.flow_chart.node.Mongo") as mongo:
        mongo.assignment = {"_client": pymongo.MongoClient()}
        main(["train", "--chart", json.dumps(FLOW_CHART)])
    os.remove("saved.csv")


PREDICT_SOURCE = {
    "id": "node-load-1",
    "type": "Load",
    "properties": {
        "name": "LoadFile",
        "class": "LoadLocal",
        "attributes": {"train_path": "iris_pred.csv", "test_path": "", "test_split": 1.0, "file_type": "csv"},
    },
}

PREDICT_DESTINY = {
    "id": "node-save-1",
    "type": "Save",
    "properties": {
        "name": "SaveFile",
        "class": "SaveLocal",
        "attributes": {"file_type": "csv", "file_name": "saved.csv", "label_column": "class"},
    },
}


def test_end_to_end_predict():
    main(["predict", "--source", json.dumps(PREDICT_SOURCE), "--destiny", json.dumps(PREDICT_DESTINY)])
    os.remove("saved.csv")
