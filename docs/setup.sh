#!/bin/bash

## Installing Microk8s ##
#source ./install_microk8s.sh


FLOWI_NAMESPACE=flowi
kubectl apply -f flowi-namespace.yml
kubectl config set-context --current --namespace=$FLOWI_NAMESPACE


## Setup secrets ##
source setup_secrets.sh


## Installing Seldon ##
cd seldon || (echo "directory seldon does not exist"; exit)
source ./setup_seldon.sh


## Installing Dask ##
kubectl config set-context --current --namespace=$FLOWI_NAMESPACE
#cd dask || (echo "directory dask does not exist"; exit)
source ./dask/install_dask.sh
#helm repo add dask https://helm.dask.org/
#helm repo update
#helm install my-dask dask/dask


## Minio ##
#kubectl apply -f minio/minio-pv.yml
#kubectl apply -f minio/minio-service.yml
#kubectl apply -f minio/minio-deployment.yml
source ./minio/setup_minio.sh

## Mongo ##
kubectl apply -f ./mongodb/mongo-deployment.yml
kubectl apply -f ./mongodb/mongo-service.yml


## Mysql ##
kubectl apply -f ./mysql/mysql-pv.yml
kubectl apply -f ./mysql/mysql-service.yml
kubectl apply -f ./mysql/mysql-deployment.yml

## Mlflow ##
kubectl apply -f ./mlflow/mlflow-deployment.yml
kubectl apply -f ./mlflow/mlflow-service.yml



## Flowi UI ##
kubectl apply -f ./flowi-ui/flowi-ui-deployment.yml
kubectl apply -f ./flowi-ui/flowi-ui-service.yml

## Airflow ##
kubectl apply -f ./airflow/airflow-rbac.yml
kubectl apply -f ./airflow/airflow-deployment.yml
kubectl apply -f ./airflow/airflow-service.yml
