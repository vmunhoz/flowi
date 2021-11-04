import numpy as np
import requests
import json
import pandas as pd


CLUSTER_IP = "10.152.183.184"

df = pd.read_csv("iris.csv")
print(df.head())
df = df.drop("class", 1)
# print(df.head())

df = df.fillna(value=0)
# print(df.values)


def predict(X):

    formData = {"data": {"ndarray": X.values.tolist()}}
    #    formData = {
    #        'instances': X.values.tolist()
    #    }
    headers = {}
    res = requests.post(
        "http://" + CLUSTER_IP + "/seldon/seldon/mnist/api/v1.0/predictions", json=formData, headers=headers
    )
    if res.status_code == 200:
        # j = res.json()
        # print(j)
        pass
    else:
        print("Failed with ", res.status_code)
        print(res.content)
        return []


for i in range(500):
    predict(df)


print("--- predicting drift")

df = pd.read_csv("iris_drift.csv")
print(df.head())
df = df.drop("class", 1)
# print(df.head())

df = df.fillna(value=0)
# print(df.values)

for i in range(500):
    predict(df)
