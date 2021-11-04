# Setup Flowi Cluster (Microk8s)

Flowi is built upon Seldon, airflow and dask
- [Kubernetes] - Open-source system for automating deployment, scaling, and management of containerized applications. v1.21
- [Seldon] - Machine Learning Management Made Easy v1.11.1
- [Istio] - Service Mesh v1.5.1
- [Knative] - ## Kubernetes-based platform to deploy and manage modern serverless workloads v0.21.0
- [Airflow] - Open-source workflow management platform
- [Dask] - Scalable analytics in Python

## Microk8s

Install Microk8s on Ubuntu.
```sh
sudo snap install microk8s --classic --channel=1.21
microk8s.status --wait-ready
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
newgrp microk8s
#sudo reboot
```
### Configure Microk8s

Configure kubectl
```sh
cd $HOME
mkdir .kube
cd .kube
microk8s config > config
```

Install dns and registry
```sh
microk8s enable dns registry helm3
```

Configure alias
```sh
sudo snap alias microk8s.kubectl kubectl
sudo snap alias microk8s.helm3 helm
```

## Seldon

Seldon requires several dependencies to run all its features (e.g. monitoring, drift detection and auto scaling).

### Istio
Microk8s has an add-on for istio. Installing manually sometimes doesn't work, not sure why.

```sh
microk8s enable istio
watch -n2 kubectl get all -n istio-system
# Wait until all services are running and with ready state
```

>seldon-gateway.yaml

```
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: seldon-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway # use istio default controller
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
```

```sh
kubectl apply -n istio-system -f seldon-gateway.yaml
```

### Seldon Namespace
>seldon-namespace.yaml
```
apiVersion: v1
kind: Namespace
metadata:
  name: seldon
  labels:
    istio-injection: disabled
```
```sd
kubectl apply -f seldon-namespace.yaml
```

### Knative
Microk8s has a Knative addon
```sh
microk8s.enable knative
kubectl get all -n knative-eventing
# Wait until all services are running and with ready state
kubectl get all -n knative-serving
# Wait until all services are running and with ready state
```

Configure Knative Event broker

>knative-broker.yaml
```
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: default
  namespace: seldon
```

```sh
kubectl create -f knative-broker.yaml
kubectl get all -n seldon
# broker has to have a url
# NAME                                  URL                                                                       AGE   READY   REASON
# broker.eventing.knative.dev/default   http://broker-ingress.knative-eventing.svc.cluster.local/seldon/default   38s   True
```

>message-dumper.yaml
```
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: message-dumper
  namespace: seldon
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
    spec:
      containers:
      - image: gcr.io/knative-releases/github.com/knative/eventing-sources/cmd/event_display
```

```sh
kubectl create -f message-dumper.yaml
kubectl get all -n seldon
```


### Seldon Core

```sh
kubectl create namespace seldon-system || echo "namespace seldon exists"
helm install seldon-core seldon-core-operator \
    --version 1.11.1 \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --namespace seldon-system \
    --set istio.enabled=true

kubectl rollout status deploy/seldon-controller-manager -n seldon-system
```



#### Ensure visibility on namespaces
Deployments are made on seldon namespace
```sh
#kubectl label ns seldon seldon.restricted=false --overwrite=true
kubectl label namespace seldon knative-eventing-injection=enabled
```

### Seldon Analytics

```sh
helm repo add seldonio https://storage.googleapis.com/seldon-charts
helm repo update

helm install seldon-core-analytics seldonio/seldon-core-analytics \
    --version 1.11.1 \
	--set grafana_prom_admin_password=password \
    --set persistence.enabled=false \
    --namespace seldon-system \
	--wait

kubectl get all -n seldon-system
```


#### Fluentd, ElasticSearch, Kibana
Microk8s has an fluentd with kibana and elastic search. They are installed under kube-system namespace.
```sh
microk8s enable fluentd
kubectl get all -n kube-system
```


## Configure Grafana

Get grafana IP to configure it with elasticsearch.
Username: admin
Password: password
```sh
kubectl get services -n seldon-system
# service/seldon-core-analytics-grafana                    ClusterIP   10.152.183.173   <none>        80/TCP     129m
# Use 10.152.183.173 ip to access grafana's dashboard
```

Select Configuration (gear) > data sources. Click on Add Ddata source and select Elasticsearch.
url: http://elasticsearch-logging.kube-system.svc.cluster.local:9200
index name: logstash-*
Time field name: @timestamp
Version: 7.0+

Then, click on Save & Test.

### Create Drift Dashboard

 1. Select dashboard > Manage
 2. Click on "New Dashboard" Click on "Painel Title" and select "edit"
 3. Click on "prometheus" and change it to Elasticsearch
 4. On A:
	 5. Query: kubernetes.pod_name: "message-dumper" and message: "\"is_drift\": 0"
	 6. Alias: Not Drift
 5. Click "+ Query"
 6. On B:
	 7. Query: kubernetes.pod_name: "message-dumper" and message: "\"is_drift\": 1"
	 8. Alias: Drift
 7. Hit Save
 8. Click On Dashboard Menu
	 9. It will ask to save the dashbord
	 10. Choose a name (e.g. Drift Detection)
 9. Enjoy :)


## Minio

Login in the dashboard using minio-admin-access-key and minio-admin-secret-key. There are secrets
```
kubectl get secret flowi-secrets -o go-template='{{range $k,$v := .data}}{{"### "}}{{$k}}{{"\n"}}{{$v|base64decode}}{{"\n\n"}}{{end}}'
```


### buckets
Create the following buckets in the dashboard:
- models
- mlflow
- flowi

### Users

Create a user in the dashboard.

Access Keyw: secret minio-access-key
Secret Key: secret minio-secret-key
Assing policy: readwrite

### Add test file

Upload flowi/tests/iris.csc  to bucket flowi under tests folder.

## Airflow

Get docker-registry ip
```
 kubectl get all -n container-registry
```

Change inside airflow

```
kubectl exec --stdin --tty -n flowi pod/airflow-deployment-669944c5f9-lrvn4 -- bash
yum install nano -y
cd dags/deploy
nano docker_build_api.sh # change ip at the bottom (two lines)
nano docker_build_batch.sh # change ip at the bottom (two lines)
```

---------------------------------------------

   [Kubernetes]: <https://kubernetes.io/>
   [Seldon]: <https://www.seldon.io/>
   [Istio]: <https://istio.io/>
   [Knative]: <https://knative.dev/docs/>
   [Airflow]: <https://airflow.apache.org/>
   [Dask]: <https://dask.org/>
