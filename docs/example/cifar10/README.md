# Cifar10



## Create yaml files

cifar10.yaml
```
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: tfserving-cifar10
  namespace: seldon
spec:
  protocol: tensorflow
  transport: rest
  predictors:
  - componentSpecs:
    - spec:
        containers:
        - args:
          - --port=8500
          - --rest_api_port=8501
          - --model_name=resnet32
          - --model_base_path=gs://seldon-models/tfserving/cifar10/resnet32
          image: tensorflow/serving
          name: resnet32
          ports:
          - containerPort: 8501
            name: http
    graph:
      name: resnet32
      type: MODEL
      endpoint:
        service_port: 8501
      logger:
        url: http://broker-ingress.knative-eventing.svc.cluster.local/seldon/default
        mode: all
    name: model
    replicas: 1

```

>cifar10cd.yaml
```
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: drift-detector
  namespace: seldon
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
    spec:
      containers:
      - image: seldonio/alibi-detect-server:0.0.1
        imagePullPolicy: IfNotPresent
        args:
        - --model_name
        - cifar10cd
        - --http_port
        - '8080'
        - --protocol
        - tensorflow.http
        - --storage_uri
        - gs://seldon-models/alibi-detect/cd/ks/cifar10
        - --reply_url
        - http://message-dumper.seldon
        - --event_type
        - io.seldon.serving.inference.drift
        - --event_source
        - io.seldon.serving.cifar10cd
        - DriftDetector
        - --drift_batch_size
        - '500'
```

>drift-trigger.yaml
```
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: drift-trigger
  namespace: seldon
spec:
  broker: default
  filter:
    attributes:
      type: io.seldon.serving.inference.request
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: drift-detector
```

## Apply to cluster

```sh
kubectl apply -f message-dumper.yaml
kubectl apply -f cifar10.yaml
# wait until it is running (watch -n2 kubectl get all -n seldon)
kubectl apply -f cifar10cd.yaml
# wait until it is running (watch -n2 kubectl get all -n seldon)
kubectl apply -f drift-trigger.yaml
# wait until it is running (watch -n2 kubectl get all -n seldon)
# Must have SUBSCRIBER_URI
# NAME                                         BROKER    SUBSCRIBER_URI                                   AGE   READY   REASON
# trigger.eventing.knative.dev/drift-trigger   default   http://drift-detector.seldon.svc.cluster.local   14s   True

kubectl get all -n seldon
```

## Configure Test code

Get istio IP and change the CLUSTER_IP variable in drift.py
```sh
kubectl -n istio-system get service istio-ingressgateway
```

python requirements
```
alibi-detect>=0.4.0
matplotlib>=3.1.1
tqdm>=4.45.0
```

>drift.py
```
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import tensorflow as tf
tf.keras.backend.clear_session()

CLUSTER_IP='10.152.183.87'

train, test = tf.keras.datasets.cifar10.load_data()
X_train, y_train = train
X_test, y_test = test

X_train = X_train.astype('float32') / 255
X_test = X_test.astype('float32') / 255
print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)
classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

def show(X):
    plt.imshow(X.reshape(32, 32, 3))
    plt.axis('off')
    plt.show()

def predict(X):
    formData = {
    'instances': X.tolist()
    }
    headers = {}
    res = requests.post('http://'+CLUSTER_IP+'/seldon/seldon/tfserving-cifar10/v1/models/resnet32/:predict', json=formData, headers=headers)
    if res.status_code == 200:
        j = res.json()
        if len(j["predictions"]) == 1:
            return classes[np.array(j["predictions"])[0].argmax()]
    else:
        print("Failed with ",res.status_code)
        return []

def drift(X):
    formData = {
    'instances': X.tolist()
    }
    headers = {}
    headers["Host"] = SERVICE_HOSTNAME_CD
    res = requests.post('http://'+CLUSTER_IP+'/', json=formData, headers=headers)
    if res.status_code == 200:
        od = res.json()
        return od
    else:
        print("Failed with ",res.status_code)
        return []


idx = 1
X = X_train[idx:idx+1]
#show(X)
predict(X)

from tqdm import tqdm
for i in tqdm(range(0,5000,100)):
    X = X_train[i:i+100]
    predict(X)



from alibi_detect.datasets import fetch_cifar10c, corruption_types_cifar10c
corruption = ['motion_blur']
X_corr, y_corr = fetch_cifar10c(corruption=corruption, severity=5, return_X_y=True)
X_corr = X_corr.astype('float32') / 255
idx = 1
X = X_corr[idx:idx+1]
#show(X)

for i in tqdm(range(0,5000,100)):
    X = X_corr[i:i+100]
    predict(X)

```

## Run test
```sh
pip install alibi-detect>=0.4.0 matplotlib>=3.1.1 tqdm>=4.45.0
python drift.py # don't forget to change the CLUSTER_IP variable
```

## Check logs
```sh
kubectl get all -n seldon
# Exampple
kubectl logs --since 3m -n seldon pod/drift-detector-00001-deployment-6c8d9f9cfc-rdlkt user-container

kubectl logs --since 1h -n seldon $(kubectl get pod -n seldon -l serving.knative.dev/configuration=message-dumper -o jsonpath='{.items[0].metadata.name}') user-container
```

## Grafana
Open Grafana to analyse the Drift Detection dashboard.
```
kubectl get svc -n seldon-system
```
