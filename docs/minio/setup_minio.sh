#!/bin/bash

kubectl apply -f minio-pv.yml
kubectl apply -f minio-service.yml
kubectl apply -f minio-deployment.yml
kubectl describe deployment minio
