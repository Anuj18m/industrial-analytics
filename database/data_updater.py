import time
import random
import pandas as pd
from datetime import datetime
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

PLANTS = ["Plant A", "Plant B", "Plant C"]

def generate_row():
    return {
        "plant": random.choice(PLANTS),
        "date": datetime.now().isoformat(timespec="seconds"),
        "output_tons": random.randint(900, 1400),
        "downtime_hours": round(random.uniform(1, 8), 2),
        "energy_kwh": random.randint(3800, 5500)
    }


def start_updater(interval=10):
    while True:
        row = generate_row()
        df = pd.DataFrame([row])

        conn = get_connection()
        df.to_sql("production_data", conn, if_exists="append", index=False)
        conn.close()

        print("Inserted:", row)
        time.sleep(interval)

if __name__ == "__main__":
    start_updater()
