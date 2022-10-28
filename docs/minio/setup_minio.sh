#!/bin/bash

kubectl apply -f minio-pv.yaml
kubectl apply -f minio-deployment.yaml
kubectl apply -f minio-service.yaml
kubectl apply -f minio-virtualservice.yaml
sleep 5
kubectl apply -f minio-job.yaml
