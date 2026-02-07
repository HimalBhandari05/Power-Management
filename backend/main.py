from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Power Monitoring Backend")


class SensorReading(BaseModel):
    timestamp: datetime
    house_id: int
    current: float


import csv
import os

DATA_FILE = "layer1_raw.csv"


@app.post("/ingest")
def ingest_reading(reading: SensorReading):
    file_exists = os.path.isfile(DATA_FILE)

    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "house_id", "current"])

        writer.writerow(
            [reading.timestamp.isoformat(), reading.house_id, reading.current]
        )

    return {"status": "ok"}
