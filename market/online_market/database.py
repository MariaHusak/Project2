from pymongo import MongoClient
from threading import Lock


class MongoDBConnection:
    _instance = None
    _lock = Lock()

    def __new__(cls, uri="mongodb://localhost:27017/", db_name="bikeshop"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_connection(uri, db_name)
            return cls._instance

    def _init_connection(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_db(self):
        return self.db
