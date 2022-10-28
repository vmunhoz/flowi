#!/bin/bash

kubectl apply -f flowi-ui-deployment.yaml
kubectl apply -f flowi-ui-service.yaml
kubectl apply -f flowi-ui-virtual-service.yaml
