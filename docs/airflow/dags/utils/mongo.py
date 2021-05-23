import os

from pymongo import MongoClient


class Mongo(object):
    def __init__(self):
        self._client = MongoClient("mongodb://mongo-service", 27017)
        _db = self._client["flowi"]
        self._collection = _db.flowi_training

    def get_models_by_version(self, flow_name: str, run_id: str, version: int or str):
        version = str(version)
        models = []
        cursor = self._collection.find({"flow_name": flow_name, "run_id": run_id, "version": version})
        for document in cursor:
            models.append(document)
        return models
