#!/bin/bash

kubectl apply -f mysql-pv.yml
kubectl apply -f mysql-deployment.yml
kubectl apply -f mysql-service.yml
