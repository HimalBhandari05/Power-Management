import os
import sys

import joblib

try:
    from fastapi import FastAPI
except Exception:
    FastAPI = None

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from layer2_generator import generate_layer2_df

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
model = joblib.load(MODEL_PATH)

app = FastAPI() if FastAPI else None


def predict_next():
    df = generate_layer2_df()

    if len(df) < 3:
        return None

    last = df.tail(3)["total_current"].values.reshape(1, -1)
    return float(model.predict(last)[0])


if app:

    @app.get("/predict/latest")
    def predict_latest():
        df = generate_layer2_df()
        if df.empty or len(df) < 4:
            return {"error": "Not enough data"}

        latest = df.iloc[-1]
        predicted_next = float(predict_next())
        predicted_total_current = round(predicted_next, 3)

        # Risk logic (backend-only)
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
            target_house = int(latest["main_contributor"])
            trigger_buzzer()
            cut_power(target_house)

        return {
            "predicted_total_current": predicted_total_current,
            "risk_level": risk_level,
            "action": action,
            "target_house": target_house,
        }
