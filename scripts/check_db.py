import sqlite3
from src.paths import DATABASE_PATH

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

print("Database location:", DATABASE_PATH)

cursor.execute("""
    SELECT
        run_id,
        prompt_version,
        accuracy,
        average_summary_score,
        summary_pass_rate
    FROM evaluation_runs
    ORDER BY created_at DESC
    LIMIT 1
""")

print("\nLatest evaluation run:")
print(cursor.fetchone())

cursor.execute("""
    SELECT
        test_case_id,
        summary_score,
        summary_pass,
        summary_reason
    FROM evaluation_cases
    ORDER BY rowid DESC
    LIMIT 5
""")

print("\nSummary evaluation records:")

for row in cursor.fetchall():
    print(row)

connection.close()