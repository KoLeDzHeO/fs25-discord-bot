import json

# Load vehicle information from the filtered list shipped with the bot
with open("filtered_vehicles.json", "r", encoding="utf-8") as f:
    VEHICLE_DATA = json.load(f)

# Map XML file key to the corresponding info dictionary
vehicle_map: dict[str, dict] = {}
for entry in VEHICLE_DATA:
    key = entry.get("nameXML") or entry.get("xml_key")
    if key:
        vehicle_map[key] = entry



def get_info_by_key(xml_key: str) -> dict:
    """Return info for the given XML key or sensible defaults."""
    return vehicle_map.get(
        xml_key,
        {
            "icon": "🛠️",
            "name": xml_key,
            "class": "Неизвестная техника",
            "fuel_capacity": None,
        },
    )
