from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")

db = client["Australian_crime_db"]
collection = db["crime_data"]

df = pd.read_csv("C:/Users/Manoj/Downloads/PostcodeData.csv")

fixed_columns = [
    "Postcode",
    "Place",
    "Offence category",
    "Subcategory"
]

month_columns = [col for col in df.columns if col not in fixed_columns]

documents = []

for _, row in df.iterrows():

    crime_data = {}

    for month in month_columns:
        crime_data[month] = int(row[month]) if pd.notna(row[month]) else 0

    doc = {
        "postcode": int(row["Postcode"]),
        "place": row["Place"],
        "offence_category": row["Offence category"],
        "subcategory": row["Subcategory"],
        "crime_data": crime_data
    }

    documents.append(doc)

# Insert in batches
batch_size = 1000

for i in range(0, len(documents), batch_size):
    collection.insert_many(documents[i:i+batch_size])

print(f"Inserted {len(documents)} documents")