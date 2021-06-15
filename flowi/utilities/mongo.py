from pprint import pprint

from pymongo import MongoClient
from bson.objectid import ObjectId

from flowi.settings import MONGO_ENDPOINT_URL, FLOW_NAME, EXPERIMENT_TRACKING, VERSION, RUN_ID


class Mongo(object):
    def __init__(self):
        self._client = MongoClient(f"mongodb://{MONGO_ENDPOINT_URL}", 27017)
        _db = self._client["flowi"]
        self._collection = _db.flowi_training

    def insert(
        self, experiment_id: str, model_uri: str, input_transformer_uri: str, output_transformer_uri: str
    ) -> str:
        document = {
            "flow_name": FLOW_NAME.lower(),
            "run_id": RUN_ID,
            "version": VERSION,
            "experiment_tracking": EXPERIMENT_TRACKING,
            "experiment_id": experiment_id,
            "model_uri": model_uri,
            "input_transformer_uri": input_transformer_uri,
            "output_transformer_uri": output_transformer_uri,
            "metrics": {},
        }
        result = self._collection.insert_one(document)
        return result.inserted_id

    def add_metric(self, mongo_id: str, metric_name: str, value: float):
        self._collection.update_one({"_id": ObjectId(mongo_id)}, [{"$set": {"metrics": {str(metric_name): value}}}])

    def stage_model(self, mongo_id: str):
        self._collection.update_one({"_id": ObjectId(mongo_id)}, [{"$set": {"staged": "true"}}])

    def get_models_by_version(self, flow_name: str, run_id: str, version: int or str):
        version = str(version)
        models = []
        cursor = self._collection.find({"flow_name": flow_name.lower(), "run_id": run_id, "version": version})
        for document in cursor:
            models.append(document)
        return models

    def show_all(self):
        cursor = self._collection.find({})
        for document in cursor:
            pprint(document)


if __name__ == "__main__":
    Mongo().show_all()
