import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection

def init_db():
    conn = get_connection()
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS production_data (
            plant TEXT,
            date TEXT,
            output_tons INTEGER,
            downtime_hours REAL,
            energy_kwh INTEGER
        )
        """)
        conn.commit()
    finally:
        conn.close()

    print("✅ Database initialized safely")

if __name__ == "__main__":
    init_db()
