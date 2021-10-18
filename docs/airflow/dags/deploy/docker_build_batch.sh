#!/bin/bash

FLOW_NAME=$1
RUN_ID=$2

## requirements.txt

echo 'flowi' > requirements.txt

## Dockerfile

echo 'FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
' > Dockerfile


aws s3 cp "s3://models/staging/${RUN_ID}/model.pkl" "model.pkl" --endpoint-url http://minio-service
aws s3 cp "s3://models/staging/${RUN_ID}/drift_detector.pkl" "drift_detector.pkl" --endpoint-url http://minio-service
aws s3 cp "s3://models/staging/${RUN_ID}/input_transformer.pkl" "input_transformer.pkl"  --endpoint-url http://minio-service
aws s3 cp "s3://models/staging/${RUN_ID}/output_transformer.pkl" "output_transformer.pkl"  --endpoint-url http://minio-service


docker build -t flowi-batch-${FLOW_NAME} .
docker tag flowi-batch-${FLOW_NAME}:latest 10.152.183.130:5000/flowi-batch-${FLOW_NAME}:latest
docker push 10.152.183.130:5000/flowi-batch-${FLOW_NAME}:latest
