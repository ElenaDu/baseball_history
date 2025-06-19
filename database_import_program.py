import pandas as pd
import sqlite3
import os

# Paths
os.makedirs("./db", exist_ok=True)
db_path = "./db/baseball_stats.db"

# Recreate DB if exists
if os.path.exists(db_path):
    answer = input("The database already exists. Do you want to recreate it? (y/n): ")
    if answer.lower() != 'y':
        print("Aborting import.")
        exit(0)
    os.remove(db_path)

# Setup DB
with sqlite3.connect(db_path, isolation_level='IMMEDIATE') as conn:
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batting_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            name TEXT,
            team_id INTEGER,
            stat TEXT,
            value REAL,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pitching_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            name TEXT,
            team_id INTEGER,
            stat TEXT,
            value REAL,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    """)

# Clean and import function

def clean_and_import(csv_path, table_name):
    df = pd.read_csv(csv_path)

    print(f"\nBefore cleaning {csv_path}: {len(df)} rows")
    print(df.head())

    # Drop rows with invalid or missing values
    df = df[pd.to_numeric(df["Value"], errors='coerce').notnull()]
    df["Value"] = pd.to_numeric(df["Value"])
    df = df.drop_duplicates()

    print(f"After cleaning {csv_path}: {len(df)} rows")
    print(df.head())

    # Insert values into tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for _, row in df.iterrows():
        year = int(row["Year"])
        stat = row["Stat"].strip()
        player = row["Player"].strip()
        team = row["Team"].strip()
        value = float(row["Value"])

        # Insert team if not already exists
        cursor.execute("INSERT OR IGNORE INTO teams (name) VALUES (?)", (team,))
        cursor.execute("SELECT id FROM teams WHERE name = ?", (team,))
        team_id = cursor.fetchone()[0]

        # Insert player stat into the appropriate table
        cursor.execute(f"""
            INSERT INTO {table_name} (year, name, team_id, stat, value)
            VALUES (?, ?, ?, ?, ?)
        """, (year, player, team_id, stat, value))

    conn.commit()
    conn.close()

# CSVs
clean_and_import("batting_stats.csv", "batting_stats")
clean_and_import("pitching_stats.csv", "pitching_stats")
