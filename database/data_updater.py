import time
import random
import pandas as pd
from datetime import datetime, timedelta
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

PLANTS = ["Plant A", "Plant B", "Plant C"]
MODE = "dataset"  # "simulation" or "dataset"
CSV_PATH = os.path.join("data", "production_data.csv")


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


def start_updater(interval=10):
    """Start data ingestion loop"""
    print(f"🚀 Starting data updater in {MODE.upper()} mode...")
    
    try:
        if MODE.lower() == "dataset":
            row_generator = load_dataset_rows()
        else:
            row_generator = None
        
        while True:
            try:
                if MODE.lower() == "dataset":
                    row = next(row_generator)
                else:
                    row = generate_row()
                
                df = pd.DataFrame([row])
                conn = get_connection()
                df.to_sql("production_data", conn, if_exists="append", index=False)
                conn.close()

                print(f"✅ Inserted [{MODE.upper()}]: {row}")
                time.sleep(interval)
            except Exception as e:
                print(f"❌ Error inserting row: {e}")
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\n⛔ Data updater stopped.")


if __name__ == "__main__":
    start_updater()
