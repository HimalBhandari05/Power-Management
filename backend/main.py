import os

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from layer2_generator import generate_layer2_df

app = FastAPI(title="Power Monitoring Backend")


class SensorReading(BaseModel):
    timestamp: datetime
    house_id: int
    current: float


import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "layer1_raw.csv")


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


@app.get("/layer2/latest")
def layer2_latest():
    df = generate_layer2_df()

    if df.empty:
        return {"error": "No data"}

    return df.iloc[-1].to_dict()


@app.get("/layer2/history")
def layer2_history(limit: int = 50):
    df = generate_layer2_df()

    if df.empty:
        return []

    return df.tail(limit).to_dict(orient="records")


import joblib

MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")
model = joblib.load(MODEL_PATH)


def predict_next():
    df = generate_layer2_df()

    if len(df) < 3:
        return None

    last = df.tail(3)["total_current"].values.reshape(1, -1)
    return float(model.predict(last)[0])


@app.get("/debug/model-status")
def model_status():
    df = generate_layer2_df()

    return {
        "layer2_rows": len(df),
        "min_total_current": float(df["total_current"].min()) if not df.empty else None,
        "max_total_current": float(df["total_current"].max()) if not df.empty else None,
        "latest_total_current": (
            float(df.iloc[-1]["total_current"]) if not df.empty else None
        ),
    }
