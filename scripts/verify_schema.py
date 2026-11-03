import sqlite3
from src.paths import DATABASE_PATH

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

for table in ["evaluation_runs", "evaluation_cases"]:
    print(f"\n--- {table} ---")

    cursor.execute(f"PRAGMA table_info({table})")

    for column in cursor.fetchall():
        print(column[1], column[2])

connection.close()