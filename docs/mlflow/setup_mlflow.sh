#/bin/bash

docker build -t mlflow .
docker tag mlflow:latest localhost:32000/mlflow:latest
docker push localhost:32000/mlflow:latest

kubectl config set-context --current --namespace=flowi
kubectl apply -f mlflow-service.yml
kubectl apply -f mlflow-deployment.yml
kubectl describe deployment mlflow-deployment
