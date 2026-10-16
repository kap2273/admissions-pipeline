from pathlib import Path
import sqlite3

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def extract_applications():
    apps = pd.read_csv(DATA_DIR / "applications.csv", dtype=str)
    return apps

def extract_sis():
    conn = sqlite3.connect(DATA_DIR / "sis.db")
    sis = pd.read_sql_query("select * from students", conn)
    conn.close()
    return sis

if __name__ == "__main__":
    apps = extract_applications()
    print(len(apps))
    print(apps.head())
    
    sis = extract_sis()
    print(len(sis))
    print(sis.head())
