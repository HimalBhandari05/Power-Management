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

        if len(df) < 4:
            return {"error": "Not enough data"}

        actual_now = float(df.iloc[-1]["total_current"])
        predicted_next = float(predict_next())

        return {
            "actual_current": actual_now,
            "predicted_next": round(predicted_next, 3),
            "prediction_error": round(predicted_next - actual_now, 3),
            "overload_risk": predicted_next > 15.0,
        }
