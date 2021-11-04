import json

import matplotlib.pyplot as plt
import numpy as np
import requests
import tensorflow as tf
from alibi_detect.datasets import fetch_cifar10c, corruption_types_cifar10c
from tqdm import tqdm

tf.keras.backend.clear_session()

CLUSTER_IP = "10.152.183.184"

train, test = tf.keras.datasets.cifar10.load_data()
X_train, y_train = train
X_test, y_test = test

X_train = X_train.astype("float32") / 255
X_test = X_test.astype("float32") / 255
print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)
classes = ("plane", "car", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck")


def show(X):
    plt.imshow(X.reshape(32, 32, 3))
    plt.axis("off")
    plt.show()


def predict(X):
    formData = {"instances": X.tolist()}
    headers = {}
    res = requests.post(
        "http://" + CLUSTER_IP + "/seldon/seldon/tfserving-cifar10/v1/models/resnet32/:predict",
        json=formData,
        headers=headers,
    )
    if res.status_code == 200:
        j = res.json()
        if len(j["predictions"]) == 1:
            return classes[np.array(j["predictions"])[0].argmax()]
    else:
        print("Failed with ", res.status_code)
        return []


#
# def drift(X):
#     formData = {"instances": X.tolist()}
#     headers = {}
#     headers["Host"] = SERVICE_HOSTNAME_CD
#     res = requests.post("http://" + CLUSTER_IP + "/", json=formData, headers=headers)
#     if res.status_code == 200:
#         od = res.json()
#         return od
#     else:
#         print("Failed with ", res.status_code)
#         return []


idx = 1
X = X_train[idx : idx + 1]
# show(X)
predict(X)

for i in tqdm(range(0, 5000, 100)):
    X = X_train[i : i + 100]
    predict(X)

corruption = ["motion_blur"]
X_corr, y_corr = fetch_cifar10c(corruption=corruption, severity=5, return_X_y=True)
X_corr = X_corr.astype("float32") / 255
idx = 1
X = X_corr[idx : idx + 1]
# show(X)

for i in tqdm(range(0, 5000, 100)):
    X = X_corr[i : i + 100]
    predict(X)
