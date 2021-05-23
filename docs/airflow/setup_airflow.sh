#/bin/bash

kubectl config set-context --current --namespace=flowi
kubectl apply -f airflow-rbac.yml
kubectl apply -f airflow-deployment.yml
kubectl apply -f airflow-service.yml
