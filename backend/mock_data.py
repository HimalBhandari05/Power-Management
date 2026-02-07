import requests
import random
import time
from datetime import datetime

API_URL = "http://127.0.0.1:8000/ingest"
HOUSE_IDS = [1, 2, 3, 4, 5]

def generate_current(house_id):
    # Simulate one heavy load house occasionally
    if house_id == random.choice(HOUSE_IDS) and random.random() < 0.2:
        return round(random.uniform(4.0, 7.0), 2)
    return round(random.uniform(0.5, 3.0), 2)

while True:
    timestamp = datetime.utcnow().isoformat()

    for house_id in HOUSE_IDS:
        payload = {
            "timestamp": timestamp,
            "house_id": house_id,
            "current": generate_current(house_id)
        }

        try:
            r = requests.post(API_URL, json=payload, timeout=1)
            print(payload, r.status_code)
        except Exception as e:
            print("Error:", e)

    time.sleep(3)
