import json
import os
from unittest import mock

import mongomock
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
                "attributes": {
                    "train_path": "tests/iris.csv",
                    "test_path": "",
                    "test_split": 0.2,
                    "file_type": "csv",
                    "target_column": "class",
                },
            },
        },
        "node-load-2": {
            "id": "node-load-2",
            "type": "Load",
            "properties": {
                "name": "LoadFile",
                "class": "LoadLocal",
                "attributes": {"train_path": "tests/iris.csv", "test_path": "", "test_split": 0.2, "file_type": "csv"},
            },
        },
        # "node-label-enc": {
        #     "id": "node-label-enc",
        #     "type": "Label",
        #     "properties": {
        #         "name": "LabelEncoder",
        #         "class": "Label",
        #         "attributes": {"target_column": "class", "is_label": True},
        #     },
        # },
        "node-fillna": {
            "id": "node-fillna",
            "type": "Preprocessing",
            "properties": {
                "name": "Fillna",
                "class": "PreprocessingDataframe",
                "attributes": {
                    "columns": [["sepal_length", "sepal_width", "petal_length", "petal_width"]],
                    "strategy": ["mean", "median"],
                },
            },
        },
        "node-standard-scaler": {
            "id": "node-standard-scaler",
            "type": "Preprocessing",
            "properties": {
                "name": "StandardScaler",
                "class": "PreprocessingDataframe",
                "attributes": {
                    # "columns": [["sepal_length", "sepal_width", "petal_length", "petal_width"]],
                    "exclude_columns": [["class"]],
                    "with_mean": True,
                    "with_std": True,
                },
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
        "node-model-tfcnn": {
            "id": "node-model-tfcnn",
            "type": "Models",
            "properties": {"name": "tfcnn", "class": "Classification", "attributes": {}},
        },
        "node-metric-accuracy": {
            "id": "node-metric-accuracy",
            "type": "Metrics",
            "properties": {"name": "accuracy", "class": "Classification", "attributes": {}},
        },
        "node-metric-accuracy2": {
            "id": "node-metric-accuracy2",
            "type": "Metrics",
            "properties": {"name": "accuracy", "class": "Classification", "attributes": {}},
        },
        "node-metric-accuracy3": {
            "id": "node-metric-accuracy3",
            "type": "Metrics",
            "properties": {"name": "accuracy", "class": "Classification", "attributes": {}},
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
        "link-load-fillna-1": {"from": {"nodeId": "node-load-1"}, "to": {"nodeId": "node-fillna"}},
        "link-load-fillna-2": {"from": {"nodeId": "node-load-2"}, "to": {"nodeId": "node-fillna"}},
        # "link-label-enc-fillna": {"from": {"nodeId": "node-label-enc"}, "to": {"nodeId": "node-fillna"}},
        "link-label-fillna-standard-scaler": {
            "from": {"nodeId": "node-fillna"},
            "to": {"nodeId": "node-standard-scaler"},
        },
        "link-standard-scaler-svc": {"from": {"nodeId": "node-standard-scaler"}, "to": {"nodeId": "node-model-svc"}},
        "link-standard-scaler-svc2": {"from": {"nodeId": "node-standard-scaler"}, "to": {"nodeId": "node-model-svc2"}},
        "link-standard-scaler-tfcnn": {
            "from": {"nodeId": "node-standard-scaler"},
            "to": {"nodeId": "node-model-tfcnn"},
        },
        "link-svc-accuracy": {"from": {"nodeId": "node-model-svc"}, "to": {"nodeId": "node-metric-accuracy"}},
        "link-svc-accuracy2": {"from": {"nodeId": "node-model-svc2"}, "to": {"nodeId": "node-metric-accuracy2"}},
        "link-svc-accuracy3": {"from": {"nodeId": "node-model-tfcnn"}, "to": {"nodeId": "node-metric-accuracy3"}},
        "link-accuracy-save": {"from": {"nodeId": "node-metric-accuracy"}, "to": {"nodeId": "node-save"}},
        "link-accuracy2-save": {"from": {"nodeId": "node-metric-accuracy2"}, "to": {"nodeId": "node-save"}},
        "link-accuracy3-save": {"from": {"nodeId": "node-metric-accuracy3"}, "to": {"nodeId": "node-save"}},
    },
}


def test_end_to_end_train(mocker):
    mocker.patch.object(flowi.settings, "FLOW_NAME", "End2End Test Flow")
    mocker.patch.object(flowi.settings, "EXPERIMENT_TRACKING", "MLflow")
    # with mock.patch("flowi.flow_chart.node.Mongo") as node_mongo:
    #     with mock.patch("flowi.flow_chart.flow_chart.Mongo") as flow_mongo:
    #         node_mongo.assignment = {"_client": pymongo.MongoClient()}
    #         flow_mongo.assignment = {"_client": pymongo.MongoClient()}
    main(["train", "--chart", json.dumps(FLOW_CHART)])
    os.remove("saved.csv")


PREDICT_SOURCE = {
    "id": "node-load-1",
    "type": "Load",
    "properties": {
        "name": "LoadFile",
        "class": "LoadLocal",
        "attributes": {"train_path": "tests/iris_pred.csv", "test_path": "", "test_split": 1.0, "file_type": "csv"},
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


# def test_end_to_end_predict(mocker):
#     mocker.patch.object(flowi.settings, "FLOW_NAME", "End2End Test Flow")
#     mocker.patch.object(flowi.settings, "EXPERIMENT_TRACKING", "MLflow")
#     # with mock.patch("flowi.flow_chart.node.Mongo") as mongo:
#     #     mongo.assignment = {"_client": pymongo.MongoClient()}
#     main(["predict", "--source", json.dumps(PREDICT_SOURCE), "--destiny", json.dumps(PREDICT_DESTINY)])
#     os.remove("saved.csv")
