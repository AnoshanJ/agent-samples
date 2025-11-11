"""
Script to migrate SQLite data to PostgreSQL.
This script downloads the SQLite database and migrates it to PostgreSQL.
"""
import os
import sqlite3
import pandas as pd
import requests
from sqlalchemy import text
from db_config import create_db_engine

# Download the SQLite database
db_url = "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
local_file = "travel2.sqlite"

print("Downloading SQLite database...")
if not os.path.exists(local_file):
    response = requests.get(db_url)
    response.raise_for_status()
    with open(local_file, "wb") as f:
        f.write(response.content)
    print("✓ SQLite database downloaded")
else:
    print("✓ SQLite database already exists")


def update_dates_sqlite(file):
    """Update dates in SQLite to current time."""
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    example_time = pd.to_datetime(
        tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    tdf["bookings"]["book_date"] = (
        pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True)
        + time_diff
    )

    datetime_columns = [
        "scheduled_departure",
        "scheduled_arrival",
        "actual_departure",
        "actual_arrival",
    ]
    for column in datetime_columns:
        tdf["flights"][column] = (
            pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
        )

    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()
    
    return tdf


def migrate_to_postgres():
    """Migrate data from SQLite to PostgreSQL."""
    print("\nUpdating dates in SQLite database...")
    tdf = update_dates_sqlite(local_file)
    print("✓ Dates updated")
    
    print("\nConnecting to PostgreSQL...")
    engine = create_db_engine()
    print("✓ Connected to PostgreSQL")
    
    print("\nMigrating tables to PostgreSQL...")
    with engine.connect() as conn:
        for table_name, df in tdf.items():
            print(f"  Migrating table: {table_name} ({len(df)} rows)...")
            # Replace NaN and "\\N" with None for proper NULL handling
            df = df.replace({"\\N": None, pd.NA: None, pd.NaT: None})
            
            # Drop table if exists
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
            conn.commit()
            
            # Write data
            df.to_sql(table_name, conn, if_exists="replace", index=False, method="multi")
            print(f"  ✓ {table_name} migrated")
    
    print("\n✅ Migration completed successfully!")
    print("\nYou can now update your .env file with the PostgreSQL connection details.")
    

if __name__ == "__main__":
    try:
        migrate_to_postgres()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nPlease check your DATABASE_URL in the .env file")
        raise
