import re
from app.db import get_db


def search_postcodes(query: str, limit: int = 10):
    db = get_db()
    escaped = re.escape(query)
    if query[0].isdigit():
        cursor = db["postcodes"].find(
            {"postcode": {"$regex": f"^{escaped}"}},
            {"_id": 0}
        ).limit(limit)
    else:
        cursor = db["postcodes"].find(
            {"place": {"$regex": escaped, "$options": "i"}},
            {"_id": 0}
        ).limit(limit)
    return list(cursor)


def get_crime_data(postcode: str, category: str):
    db = get_db()
    return db["crime_aggregated"].find_one(
        {"postcode": postcode, "category": category},
        {"_id": 0}
    )


def get_all_categories():
    db = get_db()
    return list(db["categories"].find({}, {"_id": 0}).sort("category", 1))


def get_geometry(postcode: str):
    db = get_db()
    return db["postcode_geo"].find_one(
        {"postcode": postcode},
        {"_id": 0}
    )


def get_overview(postcode: str):
    db = get_db()
    pipeline = [
        {"$match": {"postcode": postcode}},
        {"$project": {
            "category": 1, "last_year_total": 1, "total": 1, "trend": 1, "_id": 0
        }},
        {"$sort": {"last_year_total": -1}}
    ]
    return list(db["crime_aggregated"].aggregate(pipeline))
