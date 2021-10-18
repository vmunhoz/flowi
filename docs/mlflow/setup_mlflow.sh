#/bin/bash

docker build -t mlflow .
docker tag mlflow:latest localhost:32000/mlflow:latest
docker push localhost:32000/mlflow:latest

kubectl apply -f mlflow-service.yml
kubectl apply -f mlflow-deployment.yml
