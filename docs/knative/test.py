from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import tensorflow as tf

tf.keras.backend.clear_session()

CLUSTER_IP = "10.152.183.184"
SERVICE_HOSTNAME_CD = "http://drift-detector.seldon.example.com"


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
        print(j["predictions"])
        for prediction in j["predictions"]:
            print(classes[np.array(prediction)[0].argmax()])

        if len(j["predictions"]) == 1:
            return classes[np.array(j["predictions"])[0].argmax()]
    else:
        print("Failed with ", res.status_code)
        return []


def drift(X):
    formData = {"instances": X.tolist()}
    headers = {}
    headers["Host"] = SERVICE_HOSTNAME_CD
    res = requests.post("http://" + CLUSTER_IP + "/", json=formData, headers=headers)
    if res.status_code == 200:
        od = res.json()
        return od
    else:
        print("Failed with ", res.status_code)
        return []


idx = 1
X = X_train[idx : idx + 1]
show(X)
predict(X)

for i in tqdm(range(0, 500, 100)):
    X = X_train[i : i + 100]
    predict(X)
