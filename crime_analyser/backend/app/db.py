from pymongo import MongoClient
from app.config import MONGODB_URI, DB_NAME

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGODB_URI)
        _db = _client[DB_NAME]
    return _db
