#!/bin/bash

FLOW_NAME=$1
RUN_ID=$2

## Model.py

echo 'import os
import dill


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
        print("Initializing")
        self._model = self._load("model.pkl")
        self._input_transformer = self._load("input_transformer.pkl")
        self._output_transformer = self._load("output_transformer.pkl")

    @staticmethod
    def _load(file_path: str):
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                return dill.load(f)
        else:
            return DummyTransformer()

    def transform_input(self, features, feature_names):
        """
        transform input.
        Parameters
        ----------
        features : array-like
        feature_names : array of feature names (optional)
        """
        print("Running identity transform")
        return self._input_transformer.transform(X)

    def predict(self, X, features_names):
        """
        Return a prediction.

        Parameters
        ----------
        X : array-like
        feature_names : array of feature names (optional)
        """
        print("Predict called - will run identity function")
        return self._model.predict(X)

    def transform_output(self, features, feature_names):
        """
        transform output.
        Parameters
        ----------
        features : array-like
        feature_names : array of feature names (optional)
        """
        print("Running identity inverse transform")
        return self._outut_transformer.inverse_transform(X)

' > Model.py

## requirements.txt

echo 'flowi==0.3.4
seldon-core
' > requirements.txt

## Dockerfile

echo 'FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 5000

# Define environment variable
ENV MODEL_NAME Model
ENV SERVICE_TYPE MODEL

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE
' > Dockerfile


aws s3 cp "s3://models/staging/${RUN_ID}/model.pkl" "model.pkl" --endpoint-url http://minio-service
aws s3 cp "s3://models/staging/${RUN_ID}/input_transformer.pkl" "input_transformer.pkl"  --endpoint-url http://minio-service
aws s3 cp "s3://models/staging/${RUN_ID}/output_transformer.pkl" "output_transformer.pkl"  --endpoint-url http://minio-service


docker build -t flowi-${FLOW_NAME} .
docker tag flowi-${FLOW_NAME}:latest 10.152.183.130:5000/flowi-${FLOW_NAME}:latest
docker push 10.152.183.130:5000/flowi-${FLOW_NAME}:latest
