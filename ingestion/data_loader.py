import pandas as pd
from database.db import get_connection
from datetime import datetime, timedelta

def fetch_data(window_minutes=5):
    conn = get_connection()

    # Fetch all data (safe for demo-scale DB)
    df = pd.read_sql("SELECT * FROM production_data", conn)
    conn.close()

    # Convert mixed datetime formats safely
    df["date"] = pd.to_datetime(
        df["date"],
        format="mixed",
        errors="coerce"
    )

    # Drop bad rows if any
    df = df.dropna(subset=["date"])

    # Apply sliding window in pandas (NOT SQL)
    cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
    df = df[df["date"] >= cutoff_time]

    return df
