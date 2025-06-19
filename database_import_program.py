import pandas as pd
import sqlite3
import sqlalchemy as sa
import os

# Database setup
os.makedirs("./db", exist_ok=True)
db_path = "./db/baseball_stats.db"

if os.path.exists(db_path):
    answer = input("The database already exists. Do you want to recreate it? (y/n): ")
    if answer.lower() != 'y':
        print("Aborting import.")
        exit(0)
    os.remove(db_path)

# Create database and tables
with sqlite3.connect(db_path, isolation_level='IMMEDIATE') as conn:
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()

    # Batting Stats Leaders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batting_stats (
        year INTEGER,
        stat TEXT,
        player TEXT,
        team TEXT,
        value REAL
    )
    """)

    # Pitching Stats Leader Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pitching_stats (
        year INTEGER,
        stat TEXT,
        player TEXT,
        team TEXT,
        value REAL
    )
    """)

# Create a database engine for Pandas to_sql
engine = sa.create_engine('sqlite:///db/baseball_stats.db')

def clean_and_import(csv_path, table_name):
    df = pd.read_csv(csv_path)

    print(f"\nBefore cleaning {table_name}: {len(df)} rows")
    print(df.head())

    # Clean the data, drop rows where 'Value' is missing or invalid (non-numeric)
    df = df[pd.to_numeric(df["Value"], errors='coerce').notnull()]

    # Convert 'Value' column to numeric type
    df["Value"] = pd.to_numeric(df["Value"])

    # Drop duplicates 
    df = df.drop_duplicates()

    print(f"After cleaning {table_name}: {len(df)} rows")
    print(df.head())

    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Imported {len(df)} rows into '{table_name}'.")

# Import CSVs with cleaning
clean_and_import("batting_stats.csv", "batting_stats")
clean_and_import("pitching_stats.csv", "pitching_stats")
