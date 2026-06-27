import xml.etree.ElementTree as ET
import pandas as pd

xml_file = "abs_data.xml"

tree = ET.parse(xml_file)
root = tree.getroot()

ns = {
    "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
}

rows = []

for dataflow in root.findall(".//structure:Dataflow", ns):

    dataset_id = dataflow.get("id")
    version = dataflow.get("version")
    agency = dataflow.get("agencyID")

    name = dataflow.find("common:Name", ns)
    description = dataflow.find("common:Description", ns)

    rows.append({
        "dataset_id": dataset_id,
        "version": version,
        "agency": agency,
        "name": name.text if name is not None else "",
        "description": description.text if description is not None else ""
    })

df = pd.DataFrame(rows)

df.to_csv("abs_datasets.csv", index=False)
df.to_excel("abs_datasets.xlsx", index=False)

print(f"Saved {len(df)} datasets")
print("Created:")
print(" - abs_datasets.csv")
print(" - abs_datasets.xlsx")