#!/bin/bash

# istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.9.5 TARGET_ARCH=x86_64 sh -


# Installing Knative serving
kubectl apply -f https://storage.googleapis.com/knative-nightly/serving/latest/serving-core.yaml
sleep 2
kubectl apply -f https://storage.googleapis.com/knative-nightly/serving/latest/serving-core.yaml
kubectl apply -f https://storage.googleapis.com/knative-nightly/serving/latest/serving-crds.yaml
kubectl get pods -n knative-serving



# Installing Knative Eventing
kubectl apply -f https://storage.googleapis.com/knative-nightly/eventing/latest/eventing-core.yaml
sleep 2
kubectl apply -f https://storage.googleapis.com/knative-nightly/eventing/latest/eventing-core.yaml
kubectl apply -f https://storage.googleapis.com/knative-nightly/eventing/latest/eventing-crds.yaml
kubectl get pods -n knative-eventing

kubectl apply --filename https://github.com/knative-sandbox/eventing-rabbitmq/releases/latest/download/rabbitmq-broker.yaml

kubectl label namespace knative-serving istio-injection=enabled
kubectl label namespace seldon knative-eventing-injection=enabled


kubectl apply -f broker.yml
sleep 20
kubectl apply -f message-dumper.yml
sleep 60
kubectl apply -f cifar10.yml
sleep 120
kubectl apply -f cifar10cd.yml
sleep 360
kubectl apply -f trigger.yml
sleep 40

# Cluster IP
kubectl --namespace istio-system get service istio-ingressgateway

# CD Service Hostname
kubectl get ksvc drift-detector -n seldon -o jsonpath='{.status.url}' | cut -d "/" -f 3
