import json

FILE = "data/reservations.json"

def stats():
    with open(FILE, "r") as f:
        r = json.load(f)["reservations"]

    total = len(r)
    confirmed = sum(1 for x in r if x["status"] == "CONFIRMED")
    cancelled = sum(1 for x in r if x["status"] == "CANCELLED")

    return {
        "total": total,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "conversion_rate": round(confirmed / total, 2) if total else 0
    }
