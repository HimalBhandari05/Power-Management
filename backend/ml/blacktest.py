import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from layer2_generator import generate_layer2_df
from ml.predict import predict_next

TRANSFORMER_LIMIT = 15.0


def backtest(window_size=3):
    df = generate_layer2_df()

    if len(df) < window_size + 1:
        print("Not enough data for backtest")
        return

    total_currents = df["total_current"].values

    model = joblib.load("model.pkl")

    rows = [
        total_currents[i - window_size : i]
        for i in range(window_size, len(total_currents))
    ]
    X = pd.DataFrame(
        rows,
        columns=[f"total_current_lag_{i}" for i in range(1, window_size + 1)],
    )
    y = total_currents[window_size:]

    model_preds = model.predict(X)
    baseline_preds = X[f"total_current_lag_{window_size}"].to_numpy()

    model_errors = np.abs(model_preds - y)
    baseline_errors = np.abs(baseline_preds - y)

    print("=== BACKTEST RESULTS ===")
    print(f"Samples tested: {len(model_errors)}")
    print(f"Model MAE: {np.mean(model_errors):.3f}")
    print(f"Baseline MAE: {np.mean(baseline_errors):.3f}")

    if np.mean(model_errors) < np.mean(baseline_errors):
        print("✅ Model is BETTER than baseline")
    else:
        print("❌ Model is NOT better than baseline")


if __name__ == "__main__":
    backtest()
