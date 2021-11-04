# Iris Example

## Airflow
Airflow has a Iris example. Run flowiTrainIris Dag.
This will deploy an online API in seldon namespace with drift detection.

## Test model (python)
Test Iris model running the sample python code.
```
python iris.py
```

## Logs
Get drift-detetion-iris and message-dumper pod names by running the following command:
```
kubectl get all -n seldon
```

The query logs. Be sure to change pod's name.
```
# Drift detection logs
kubectl logs --since 1h -n seldon pod/drift-detector-mnist-00001-deployment-6d8b649fc9-bmgtx user-container

# Message dumper logs
kubectl logs --since 1h -n seldon pod/message-dumper-00001-deployment-57bb9446bc-lbksx user-container
```

## Grafana
Open Grafana to analyse the Drift Detection dashboard.
```
kubectl get svc -n seldon-system
```
