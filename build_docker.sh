#!/bin/bash

# flowi
docker build -t flowi .
docker tag flowi:latest localhost:32000/flowi:latest
docker push localhost:32000/flowi:latest

# airflow
cd ./docs/airflow
docker build -t airflow .
docker tag airflow:latest localhost:32000/airflow:latest
docker push localhost:32000/airflow:latest


# mlflow
cd ../mlflow
docker build -t mlflow .
docker tag mlflow:latest localhost:32000/mlflow:latest
docker push localhost:32000/mlflow:latest
