#!/bin/bash

FLOW_NAME=$1
RUN_ID=$2

## Model.py

echo 'import os
import dill
import numpy as np
from typing import Union, List
import logging
import pandas as pd
import tensorflow as tf


class DummyTransformer(object):

    @staticmethod
    def predict(X):
        return X

    @staticmethod
    def transform(features):
        return features

    @staticmethod
    def inverse_transform(features):
        return features


class Model(object):
    """
    Model template. You can load your model parameters in __init__ from a location accessible at runtime
    """

    def __init__(self):
        self._log = logging.getLogger("model-logger")
        self._log.info("Initializing")
        self._model = None
        self.loaded = False
        self.graph = None
        self._input_transformer = self._load("input_transformer.pkl")
        self._output_transformer = self._load("output_transformer.pkl")
        self._columns = self._load("columns.pkl")
        self._log.info(self._columns)

    def load(self):
        self._log.info(f"Loading model for pid {os.getpid()}")
        self.graph = tf.compat.v1.get_default_graph()
        with self.graph.as_default():
            self._model = self._load("model.pkl")
        self.loaded = True
        self._log.info("Loaded model")

    def health_status(self):
        return {"status": "ok"}

    def _load(self, file_path: str):
        self._log.info(f"Loading {file_path}")
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                return dill.load(f)
        else:
            self._log.info(f"Loading dummy {file_path}")
            return DummyTransformer()

    def transform_input(self, X: np.ndarray) -> Union[np.ndarray, List, str, bytes]:
        self._log.debug("Transforming Input")
        return self._input_transformer.transform(X)

    def predict(self, X, features_names):
        if not self.loaded:
            self._log.debug("Not loaded")
            self.load()

        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X, columns=self._columns)

        X = self.transform_input(X)

        self._log.info("Predicting")
        with self.graph.as_default():
            y = self._model.predict(X)

        y = self.transform_output(y)
        return y

    def transform_output(self, X: np.ndarray) -> Union[np.ndarray, List, str, bytes]:
        self._log.debug("Transforming Output")
        return self._output_transformer.inverse_transform(X)

' > Model.py

## requirements.txt

echo 'flowi==0.3.12
seldon-core==1.11.2
' > requirements.txt

## Dockerfile

echo 'FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

EXPOSE 6000
EXPOSE 9000

# Define environment variable
ENV MODEL_NAME Model
ENV SERVICE_TYPE MODEL

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE
' > Dockerfile


aws s3 cp "s3://models/staging/${RUN_ID}/model.pkl" "model.pkl" --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/columns.pkl" "columns.pkl" --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/input_transformer.pkl" "input_transformer.pkl"  --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/output_transformer.pkl" "output_transformer.pkl"  --endpoint-url http://minio


docker build -t flowi-${FLOW_NAME} .
docker tag flowi-${FLOW_NAME}:latest 10.152.183.194:5000/flowi-${FLOW_NAME}:latest
docker push 10.152.183.194:5000/flowi-${FLOW_NAME}:latest
