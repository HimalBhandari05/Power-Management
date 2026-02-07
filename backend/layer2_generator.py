import pandas as pd
from datetime import datetime

# ================= CONFIG =================

LAYER1_FILE = "layer1_raw.csv"
LAYER2_FILE = "layer2_system.csv"

TRANSFORMER_CURRENT_LIMIT = 15.0  # amps
PEAK_HOURS = range(18, 22)  # 18–21 inclusive

# ==========================================


def generate_layer2():
    # Load Layer 1 data
    df = pd.read_csv(LAYER1_FILE)

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Group by timestamp (one row per system snapshot)
    grouped = df.groupby("timestamp")

    records = []
    prev_total_current = None

    for timestamp, group in grouped:
        hour = timestamp.hour
        is_peak_hour = hour in PEAK_HOURS

        total_current = group["current"].sum()

        # Rate of change
        if prev_total_current is None:
            current_change_rate = 0.0
        else:
            current_change_rate = total_current - prev_total_current

        overload_flag = total_current > TRANSFORMER_CURRENT_LIMIT

        # Main contributor (house drawing most current)
        main_contributor = int(
            group.loc[group["current"].idxmax(), "house_id"]
        )

        records.append({
            "timestamp": timestamp.isoformat(),
            "hour": hour,
            "is_peak_hour": is_peak_hour,
            "total_current": round(total_current, 3),
            "current_change_rate": round(current_change_rate, 3),
            "overload_flag": overload_flag,
            "main_contributor": main_contributor
        })

        prev_total_current = total_current

    # Create Layer 2 DataFrame
    layer2_df = pd.DataFrame(records)

    # Save
    layer2_df.to_csv(LAYER2_FILE, index=False)

    print(f"Layer 2 generated → {LAYER2_FILE}")
    print(layer2_df.tail())


if __name__ == "__main__":
    generate_layer2()
