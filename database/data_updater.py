import time
import random
import threading
import pandas as pd
from datetime import datetime, timedelta
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

PLANTS = ["Plant A", "Plant B", "Plant C"]
MODE = "dataset"  # "simulation" or "dataset"
CSV_PATH = os.path.join("data", "production_data.csv")
_updater_thread = None


def generate_row():
    """Generate random synthetic data (simulation mode)"""
    return {
        "plant": random.choice(PLANTS),
        "date": datetime.now().isoformat(timespec="seconds"),
        "output_tons": random.randint(900, 1400),
        "downtime_hours": round(random.uniform(1, 8), 2),
        "energy_kwh": random.randint(3800, 5500)
    }


def load_dataset_rows():
    """Load and replay production_data.csv rows (dataset mode)"""
    try:
        df = pd.read_csv(CSV_PATH)
        df["date"] = pd.to_datetime(df["date"])
        
        # Replay data with current timestamps, cycling through dataset
        base_time = datetime.now()
        idx = 0
        
        while True:
            row_idx = idx % len(df)
            row = df.iloc[row_idx].to_dict()
            
            # Simple increment in minutes instead of complex offset
            row["date"] = (base_time + timedelta(minutes=idx)).isoformat(timespec="seconds")
            
            yield row
            idx += 1
    except Exception as e:
        print(f"Error loading dataset: {e}. Falling back to simulation mode.")
        while True:
            yield generate_row()


def update_data_once(row_generator=None):
    """Insert a single production row into the database."""
    if MODE.lower() == "dataset":
        if row_generator is None:
            row_generator = load_dataset_rows()
        row = next(row_generator)
    else:
        row = generate_row()

    df = pd.DataFrame([row])
    conn = get_connection()
    try:
        df.to_sql("production_data", conn, if_exists="append", index=False)
    finally:
        conn.close()

    print(f"✅ Data inserted successfully [{MODE.upper()}]: {row}")
    return row_generator


def _run_updater_loop(interval=10):
    """Background loop that keeps inserting data."""
    print(f"🚀 Starting data updater in {MODE.upper()} mode...")

    row_generator = load_dataset_rows() if MODE.lower() == "dataset" else None

    while True:
        try:
            row_generator = update_data_once(row_generator)
        except Exception as e:
            print(f"❌ Updater error: {e}")
        time.sleep(interval)


def start_updater(interval=10):
    """Start the updater in a daemon thread and return the thread."""
    global _updater_thread

    if _updater_thread is not None and _updater_thread.is_alive():
        return _updater_thread

    _updater_thread = threading.Thread(
        target=_run_updater_loop,
        kwargs={"interval": interval},
        daemon=True,
    )
    _updater_thread.start()
    return _updater_thread


if __name__ == "__main__":
    thread = start_updater()
    try:
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Data updater stopped.")
