from pprint import pprint

from pymongo import MongoClient

from flowi.settings import MONGO_ENDPOINT_URL, FLOW_NAME, EXPERIMENT_TRACKING, VERSION, RUN_ID


class Mongo(object):
    def __init__(self):
        self._client = MongoClient(f"mongodb://{MONGO_ENDPOINT_URL}", 27017)
        _db = self._client["flowi"]
        self._collection = _db.flowi_training

    def insert(self, experiment_id: str) -> str:
        document = {
            "flow_name": FLOW_NAME,
            "run_id": RUN_ID,
            "version": VERSION,
            "experiment_tracking": EXPERIMENT_TRACKING,
            "experiment_id": experiment_id,
            "metrics": {},
        }
        result = self._collection.insert_one(document)
        return result.inserted_id

    def update(self, mongo_id: str, metric_name: str, value: float):
        self._collection.update_one({"_id": mongo_id}, [{"$set": {"metrics": {str(metric_name): value}}}])

    def show_all(self):
        cursor = self._collection.find({})
        for document in cursor:
            pprint(document)


if __name__ == "__main__":
    Mongo().show_all()
