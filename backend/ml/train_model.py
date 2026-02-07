import os
import sys

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))
from layer2_generator import generate_layer2_df

LAGS = 3


def add_lags(df):
    for lag in range(1, LAGS + 1):
        df[f"total_current_lag_{lag}"] = df["total_current"].shift(lag)
    return df.dropna()


def train():
    df = generate_layer2_df()

    df = add_lags(df)

    X = df[[f"total_current_lag_{i}" for i in range(1, LAGS + 1)]]
    y = df["total_current"]

    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)

    model.fit(X, y)

    model_path = os.path.join(BASE_DIR, "model.pkl")
    joblib.dump(model, model_path)
    print("Model trained and saved")


if __name__ == "__main__":
    train()
