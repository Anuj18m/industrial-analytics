import sqlite3
import os

DB_PATH = os.path.join("database", "industrial.db")

def get_connection():
    return sqlite3.connect(DB_PATH)
