#/bin/bash

kubectl config set-context --current --namespace=flowi
kubectl apply -f mysql-pv.yml
kubectl apply -f mysql-deployment.yml
kubectl describe deployment mysql
