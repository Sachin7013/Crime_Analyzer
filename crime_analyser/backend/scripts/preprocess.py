"""
One-time preprocessing script.
Reads raw crime_data from MongoDB and creates optimized collections:
  - crime_aggregated  (one doc per postcode + category, with pre-computed arrays)
  - postcodes         (for autocomplete search)
  - categories        (21 categories with their subcategory names)
  - postcode_geo      (centroid coordinates via pgeocode)
"""

import math
import sys
from pymongo import MongoClient

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_KEYS = [f"{m} {y}" for y in range(1995, 2026) for m in MONTHS]


def main():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Australian_crime_db"]
    raw = db["crime_data"]

    total_raw = raw.count_documents({})
    if total_raw == 0:
        print("ERROR: crime_data collection is empty. Load the CSV first.")
        sys.exit(1)

    print(f"Reading {total_raw} raw documents...")
    all_docs = list(raw.find())

    # Verify month keys exist
    sample_keys = list(all_docs[0].get("crime_data", {}).keys())
    if MONTH_KEYS[0] not in sample_keys:
        print(f"WARNING: Expected key '{MONTH_KEYS[0]}' not found. Found: {sample_keys[:3]}")

    # Group by (postcode, category)
    groups = {}
    postcodes = {}

    for doc in all_docs:
        pc = str(doc["postcode"])
        cat = doc["offence_category"]
        sub = doc["subcategory"]
        place = doc.get("place", "")

        key = (pc, cat)
        if key not in groups:
            groups[key] = {"place": place, "subcategories": []}

        crime_data = doc.get("crime_data", {})
        monthly = []
        for mk in MONTH_KEYS:
            v = crime_data.get(mk, 0)
            if isinstance(v, float) and math.isnan(v):
                v = 0
            monthly.append(int(v))

        groups[key]["subcategories"].append({"name": sub, "monthly": monthly})
        postcodes[pc] = place

    print(f"Grouped into {len(groups)} (postcode, category) pairs")
    print(f"Found {len(postcodes)} unique postcodes")

    # Build aggregated documents
    crime_docs = []
    categories = {}

    for (pc, cat), data in groups.items():
        monthly = [0] * 372
        for sub in data["subcategories"]:
            for i in range(372):
                monthly[i] += sub["monthly"][i]

        yearly = []
        for y_idx, year in enumerate(range(1995, 2026)):
            start = y_idx * 12
            total = sum(monthly[start:start + 12])
            yearly.append({"year": year, "total": total})

        grand_total = sum(monthly)
        last_year_total = yearly[-1]["total"]

        last_5yr = sum(y["total"] for y in yearly[-5:])
        prev_5yr = sum(y["total"] for y in yearly[-10:-5])
        pct_change = round(((last_5yr - prev_5yr) / prev_5yr) * 100) if prev_5yr > 0 else 0

        if pct_change < -5:
            direction = "down"
        elif pct_change > 5:
            direction = "up"
        else:
            direction = "steady"

        crime_docs.append({
            "postcode": pc,
            "place": data["place"],
            "category": cat,
            "monthly": monthly,
            "yearly": yearly,
            "total": grand_total,
            "last_year_total": last_year_total,
            "trend": {"direction": direction, "pct_change_5yr": pct_change},
            "subcategories": [
                {"name": s["name"], "monthly": s["monthly"]}
                for s in data["subcategories"]
            ]
        })

        if cat not in categories:
            categories[cat] = set()
        for sub in data["subcategories"]:
            categories[cat].add(sub["name"])

    # Write crime_aggregated
    print("Writing crime_aggregated...")
    db.drop_collection("crime_aggregated")
    if crime_docs:
        db["crime_aggregated"].insert_many(crime_docs)
        db["crime_aggregated"].create_index([("postcode", 1), ("category", 1)])
    print(f"  {len(crime_docs)} documents")

    # Write postcodes
    print("Writing postcodes...")
    db.drop_collection("postcodes")
    pc_docs = [{"postcode": pc, "place": pl} for pc, pl in sorted(postcodes.items())]
    if pc_docs:
        db["postcodes"].insert_many(pc_docs)
        db["postcodes"].create_index("postcode")
        db["postcodes"].create_index([("place", 1)])
    print(f"  {len(pc_docs)} documents")

    # Write categories
    print("Writing categories...")
    db.drop_collection("categories")
    cat_docs = [
        {"category": cat, "subcategories": sorted(list(subs))}
        for cat, subs in sorted(categories.items())
    ]
    if cat_docs:
        db["categories"].insert_many(cat_docs)
    print(f"  {len(cat_docs)} documents")

    # Generate coordinates with pgeocode
    print("Generating postcode coordinates...")
    try:
        import pgeocode
        nomi = pgeocode.Nominatim("au")
        geo_docs = []
        for pc in sorted(postcodes.keys()):
            result = nomi.query_postal_code(pc)
            lat, lon = result.latitude, result.longitude
            if not (math.isnan(lat) or math.isnan(lon)):
                geo_docs.append({
                    "postcode": pc,
                    "centroid": [round(float(lon), 6), round(float(lat), 6)],
                    "boundary": None
                })

        db.drop_collection("postcode_geo")
        if geo_docs:
            db["postcode_geo"].insert_many(geo_docs)
            db["postcode_geo"].create_index("postcode")
        print(f"  {len(geo_docs)} postcodes geocoded")
    except ImportError:
        print("  pgeocode not installed - run: pip install pgeocode")
        print("  Skipping geometry generation")
    except Exception as e:
        print(f"  Geometry error: {e}")

    print("\nPreprocessing complete!")
    print("Start the server:")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")
    print("Then open: http://localhost:8000")


if __name__ == "__main__":
    main()
