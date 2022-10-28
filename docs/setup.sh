#!/bin/bash

## Installing Microk8s ##
#source ./install_microk8s.sh


FLOWI_NAMESPACE=flowi
kubectl apply -f flowi-namespace.yml
kubectl config set-context --current --namespace=$FLOWI_NAMESPACE


## Setup secrets ##
source setup_secrets.sh

cd istio || (echo "directory istio does not exist"; exit)
kubectl apply -f gateway.yaml


## Installing Seldon ##
cd seldon || (echo "directory seldon does not exist"; exit)
source ./setup_seldon.sh


## Installing Dask ##
cd dask
kubectl config set-context --current --namespace=$FLOWI_NAMESPACE
#cd dask || (echo "directory dask does not exist"; exit)
source install_dask.sh
#helm repo add dask https://helm.dask.org/
#helm repo update
#helm install my-dask dask/dask


## Minio ##
cd ../minio
#kubectl apply -f minio/minio-pv.yaml
#kubectl apply -f minio/minio-service.yaml
#kubectl apply -f minio/minio-deployment.yaml
source setup_minio.sh

## Mongo ##
cd ../mongodb
#kubectl apply -f ./mongodb/mongo-deployment.yml
#kubectl apply -f ./mongodb/mongo-service.yml
source setup_mongodb.sh


## Mysql ##
cd ../mysql
#kubectl apply -f ./mysql/mysql-pv.yml
#kubectl apply -f ./mysql/mysql-service.yml
#kubectl apply -f ./mysql/mysql-deployment.yml
source setup_mysql.sh

## Mlflow ##
cd ../mlflow
#kubectl apply -f ./mlflow/mlflow-deployment.yml
#kubectl apply -f ./mlflow/mlflow-service.yml
source setup_mlflow.sh



## Flowi UI ##
cd ../flowi-ui
#kubectl apply -f ./flowi-ui/flowi-ui-deployment.yaml
#kubectl apply -f ./flowi-ui/flowi-ui-service.yaml
source setup_flowi-ui.sh

## Airflow ##
cd ../airflow
#kubectl apply -f ./airflow/airflow-rbac.yml
#kubectl apply -f ./airflow/airflow-deployment.yml
#kubectl apply -f ./airflow/airflow-service.yml
source setup_airflow.sh
