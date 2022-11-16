#!/bin/bash

docker build -t airflow .
docker tag airflow:latest localhost:32000/airflow:latest
docker push localhost:32000/airflow:latest

kubectl apply -f airflow-rbac.yml
kubectl apply -f airflow-deployment.yml
kubectl apply -f airflow-service.yml
kubectl apply -f airflow-virtual-service.yaml
