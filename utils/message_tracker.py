import json
from pathlib import Path

DATA_FILE = Path("data/messages.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_ids():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_ids(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_id(key):
    data = load_ids()
    return data.get(key)


def set_id(key, value):
    data = load_ids()
    data[key] = str(value)
    save_ids(data)
