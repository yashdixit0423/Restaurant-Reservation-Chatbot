import re
import os
import requests

SCALEDOWN_URL = "https://api.scaledown.xyz/compress/raw/"
SCALEDOWN_KEY = os.getenv("SCALEDOWN_API_KEY")

def extract_intent(text: str) -> dict:
    t = text.lower()

    if any(w in t for w in ["book", "reserve", "table"]):
        intent = "book"
    elif "cancel" in t:
        intent = "cancel"
    elif "menu" in t:
        intent = "menu"
    elif any(w in t for w in ["open", "close", "hour"]):
        intent = "hours"
    else:
        intent = "help"

    date = None
    time = None
    people = None

    d = re.search(r"\d{4}-\d{2}-\d{2}", t)
    if d:
        date = d.group()

    tm = re.search(r"\d{1,2}:\d{2}", t)
    if tm:
        time = tm.group()

    p = re.search(r"(\d+)\s*(people|guests|persons)", t)
    if p:
        people = int(p.group(1))

    return {
        "intent": intent,
        "date": date,
        "time": time,
        "people": people
    }

def scaledown_compress(text: str) -> str:
    if not SCALEDOWN_KEY:
        return text

    headers = {
        "x-api-key": SCALEDOWN_KEY,
        "Content-Type": "application/json"
    }

    payload = {"text": text, "ratio": 0.3}

    try:
        r = requests.post(SCALEDOWN_URL, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        return r.json().get("compressed_text", text)
    except requests.RequestException:
        return text
