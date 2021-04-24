#/bin/bash

FLOWI_NAMESPACE=flowi

kubectl apply -f flowi-namespace.yml
kubectl config set-context --current --namespace=$FLOWI_NAMESPACE

mkdir /tmp/flowi

# Istio for Flowi ##
cd istio
kubectl apply -f flowi-virtual-service.yml

kubectl label namespace default istio-injection=enable

## Flowi UI ##
cd flowi-ui
kubectl apply -f flowi-ui-deployment.yml
kubectl apply -f flowi-ui-service.yml

## Airflow ##
cd airflow
kubectl apply -f airflow-deployment.yml
kubectl apply -f airflow-service.yml


## Dask ##
kubectl create namespace dask
helm repo add dask https://helm.dask.org/
helm repo update
helm install my-dask dask/dask
