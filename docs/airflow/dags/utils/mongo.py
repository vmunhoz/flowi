import os

from pymongo import MongoClient
from bson.objectid import ObjectId


class Mongo(object):
    def __init__(self):
        self._client = MongoClient("mongodb://mongo", 27017)
        _db = self._client["flowi"]
        self._collection = _db.flowi_training

    def get_staged_model(self, flow_name: str, run_id: str):
        flow_name = flow_name.lower()
        staged_model = self._collection.find_one({"flow_name": flow_name, "run_id": run_id, "staged": "true"})
        print(staged_model)
        return staged_model

    def get_deployed_model(self, flow_name: str):
        flow_name = flow_name.lower()
        deployed_model = self._collection.find_one({"flow_name": flow_name, "deployed": "true"})
        print(deployed_model)
        return deployed_model

    def deploy_model(self, mongo_id: str):
        self._collection.update_one({"_id": ObjectId(mongo_id)}, [{"$set": {"deployed": "true"}}])

    def undeploy_model(self, mongo_id: str):
        self._collection.update_one({"_id": ObjectId(mongo_id)}, {"$unset": {"deployed": ""}})

    def unstage_model(self, mongo_id: str):
        self._collection.update_one({"_id": ObjectId(mongo_id)}, {"$unset": {"staged": ""}})
