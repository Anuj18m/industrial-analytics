import sqlite3
import os

DB_PATH = "industrial.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
