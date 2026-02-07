import json
import os
import time

FILE = os.path.join("data", "waitlist.json")

def add(entry):
    with open(FILE, "r") as f:
        data = json.load(f)

    entry["id"] = f"W{int(time.time())}"
    data["waitlist"].append(entry)

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
