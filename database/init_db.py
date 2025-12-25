import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

CSV_PATH = os.path.join("data", "production_data.csv")

def init_database():
    df = pd.read_csv(CSV_PATH)
    df["date"] = pd.to_datetime(df["date"])

    conn = get_connection()
    df.to_sql("production_data", conn, if_exists="replace", index=False)
    conn.close()

    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_database()
