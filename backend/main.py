import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from layer2_generator import generate_layer2_df
import pandas as pd

app = FastAPI(title="Power Monitoring Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    last = df.tail(3)["total_current"].values
    X = pd.DataFrame(
        [last],
        columns=["total_current_lag_1", "total_current_lag_2", "total_current_lag_3"],
    )
    return float(model.predict(X)[0])


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


TRANSFORMER_LIMIT = 15.0
WARNING_THRESHOLD = 0.6 * TRANSFORMER_LIMIT


def trigger_buzzer():
    print("BUZZER: ON (stub)")


def cut_power(house_id: int):
    print(f"CUT_POWER: house_id={house_id} (stub)")


@app.get("/predict/latest")
def predict_latest():
    df = generate_layer2_df()
    if df.empty or len(df) < 4:
        return {"error": "Not enough data"}

    predicted_next = predict_next()
    if predicted_next is None:
        return {"error": "Not enough data"}

    predicted_total_current = round(float(predicted_next), 3)

    if predicted_total_current < WARNING_THRESHOLD:
        risk_level = "SAFE"
        action = "NONE"
        target_house = None
    elif predicted_total_current < TRANSFORMER_LIMIT:
        risk_level = "WARNING"
        action = "NOTIFY"
        target_house = None
        trigger_buzzer()
    else:
        risk_level = "CRITICAL"
        action = "CUT_POWER"
        target_house = int(df.iloc[-1]["main_contributor"])
        trigger_buzzer()
        cut_power(target_house)

    return {
        "predicted_total_current": predicted_total_current,
        "risk_level": risk_level,
        "action": action,
        "target_house": target_house,
    }
