#!/bin/bash

# Install microk8s (kubernetes)
#sudo snap install microk8s --classic
#sudo usermod -a -G microk8s $USER
#sudo chown -f -R $USER ~/.kube
#su - $USER
#sudo microk8s status --wait-ready
#
## Setup microk8s
#microk8s enable dashboard istio helm3 registry


#microk8s.kubectl create namespace seldon
kubectl apply -f seldon-namespace.yml
microk8s.kubectl config set-context $(microk8s.kubectl config current-context) --namespace=seldon

#microk8s.kubectl label namespace seldon istio-injection=enabled
microk8s.kubectl apply -f istio/seldon-gateway.yaml

microk8s.kubectl create namespace seldon-system
microk8s.helm3 install seldon-core seldon-core-operator --repo https://storage.googleapis.com/seldon-charts --set istio.enabled=true --set usageMetrics.enabled=true --namespace seldon-system

microk8s.kubectl rollout status deploy/seldon-controller-manager -n seldon-system

# Grafana (user=admin, password=password)
microk8s.helm3 install seldon-core-analytics seldon-core-analytics \
   --repo https://storage.googleapis.com/seldon-charts \
   --namespace seldon-system

#microk8s.kubectl apply -f iris.yaml
#
#INGRESS_HOST=microk8s.kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.clusterIP}'
#
## Wait for container to spun up
#sleep 10
#
## prediction
#curl -X POST http://$INGRESS_HOST/seldon/seldon/iris-model/api/v1.0/predictions \
#        -H 'Content-Type: application/json' \
#        -d '{ "data": { "ndarray": [[1,2,3,4]] } }'
#
#
#curl -X POST http://10.152.183.128/seldon/seldon/iris-model/api/v1.0/predictions \
#        -H 'Content-Type: application/json' \
#        -d '{ "data": { "ndarray": [[1,2,3,4]] } }'
#
#
#
## swagger docs
#curl -X GET  http://$INGRESS_HOST/seldon/seldon/iris-model/api/v1.0/doc/
#
#http://10.152.183.128/seldon/seldon/iris-model/api/v1.0/doc/
#
#
#
#curl -X POST http://10.152.183.54/seldon/seldon/iris-model/api/v1.0/predictions -H 'Content-Type: application/json' -d '{ "data": { "ndarray": [[1,2,3,4]] } }'
#
#
#curl -X POST http://10.152.183.54/seldon/seldon/iris-model/api/v1.0/predictions -H 'Content-Type: application/json' -d '[[1.1,2.2,3.2,4.2]]'
#
#
#
## bento
#curl -X POST http://10.152.183.128/seldon/seldon/bento/api/v1.0/predictions -H 'Content-Type: application/json' -d '[[1.1,2.2,3.2,4.2]]'
