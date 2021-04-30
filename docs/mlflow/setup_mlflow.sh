#/bin/bash

kubectl config set-context --current --namespace=flowi
kubectl apply -f mlflow-service.yml
kubectl apply -f mlflow-deployment.yml
kubectl describe deployment mlflow-deployment
