import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAYER1_FILE = os.path.join(BASE_DIR, "layer1_raw.csv")
TRANSFORMER_CURRENT_LIMIT = 15.0
PEAK_HOURS = range(18, 22)


def generate_layer2_df():
    df = pd.read_csv(LAYER1_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    grouped = df.groupby("timestamp")

    records = []
    prev_total_current = None

    for timestamp, group in grouped:
        total_current = group["current"].sum()

        if prev_total_current is None:
            current_change_rate = 0.0
        else:
            current_change_rate = total_current - prev_total_current

        overload_flag = total_current > TRANSFORMER_CURRENT_LIMIT

        main_contributor = int(group.loc[group["current"].idxmax(), "house_id"])

        records.append(
            {
                "timestamp": timestamp.isoformat(),
                "hour": timestamp.hour,
                "is_peak_hour": timestamp.hour in PEAK_HOURS,
                "total_current": round(total_current, 3),
                "current_change_rate": round(current_change_rate, 3),
                "overload_flag": overload_flag,
                "main_contributor": main_contributor,
            }
        )

        prev_total_current = total_current

    return pd.DataFrame(records)