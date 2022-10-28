#!/bin/bash

FLOW_NAME=$1
RUN_ID=$2

## requirements.txt

echo 'flowi' > requirements.txt

## Dockerfile

echo 'FROM psilvaleo/flowi

#WORKDIR /app
#COPY requirements.txt /app
#RUN pip install -r requirements.txt
COPY . .
' > Dockerfile

mkdir drift_detector

aws s3 cp "s3://models/staging/${RUN_ID}/model.pkl" "model.pkl" --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/columns.pkl" "columns.pkl" --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/KSDrift.pickle" "drift_detector/KSDrift.pickle" --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/meta.pickle" "drift_detector/meta.pickle" --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/input_transformer.pkl" "input_transformer.pkl"  --endpoint-url http://minio
aws s3 cp "s3://models/staging/${RUN_ID}/output_transformer.pkl" "output_transformer.pkl"  --endpoint-url http://minio


docker build -t flowi-batch-${FLOW_NAME} .
docker tag flowi-batch-${FLOW_NAME}:latest 10.152.183.203:5000/flowi-batch-${FLOW_NAME}:latest
docker push 10.152.183.203:5000/flowi-batch-${FLOW_NAME}:latest
