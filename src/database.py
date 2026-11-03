import sqlite3
from datetime import datetime
from .paths import DATABASE_PATH

DB_PATH = str(DATABASE_PATH)

def initialize_database():
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                run_id TEXT PRIMARY KEY,
                prompt_version TEXT NOT NULL,
                total_cases INTEGER NOT NULL,
                successful_cases INTEGER NOT NULL,
                failed_cases INTEGER NOT NULL,
                accuracy REAL,
                average_summary_score REAL,
                summary_pass_rate REAL,
                average_latency_seconds REAL,
                total_tokens INTEGER,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_cases (
                run_id TEXT NOT NULL,
                test_case_id TEXT NOT NULL,
                expected_category TEXT,
                predicted_category TEXT,
                category_pass INTEGER,
                summary_score INTEGER,
                summary_pass INTEGER,
                summary_reason TEXT,
                latency_seconds REAL,
                status TEXT NOT NULL,
                error TEXT,
                PRIMARY KEY (run_id, test_case_id),
                FOREIGN KEY (run_id)
                REFERENCES evaluation_runs(run_id)
                ON DELETE CASCADE
            )
        """)
        connection.commit()
    finally:
        connection.close()

def save_evaluation(report):
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.cursor()
        created_at = report.get("created_at", datetime.utcnow().isoformat())
        average_summary_score = report.get("average_summary_score")
        summary_pass_rate = report.get("summary_pass_rate")
        cursor.execute("""
            INSERT INTO evaluation_runs (
                run_id,
                prompt_version,
                total_cases,
                successful_cases,
                failed_cases,
                accuracy,
                average_latency_seconds,
                total_tokens,
                created_at,
                average_summary_score,
                summary_pass_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report["run_id"],
            report["prompt_version"],
            report["total_cases"],
            report["successful_cases"],
            report["failed_cases"],
            report["accuracy"],
            report["average_latency_seconds"],
            report["total_tokens"],
            created_at,
            average_summary_score,
            summary_pass_rate
        ))
        for result in report["results"]:
            cursor.execute("""
                INSERT INTO evaluation_cases (
                    run_id,
                    test_case_id,
                    expected_category,
                    predicted_category,
                    category_pass,
                    latency_seconds,
                    status,
                    error,
                    summary_score,
                    summary_pass,
                    summary_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report["run_id"],
                result["test_case_id"],
                result["expected_category"],
                result["predicted_category"],
                int(result["category_pass"]) if result["category_pass"] is not None else None,
                result["latency_seconds"],
                result["status"],
                result["error"],
                result.get("summary_score"),
                int(result["summary_pass"])
                    if result.get("summary_pass") is not None else None,
                result.get("summary_reason")
            ))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def migrate_database():
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        migrations = {
            "evaluation_runs": {
                "average_summary_score": "REAL",
                "summary_pass_rate": "REAL"
            },
            "evaluation_cases": {
                "summary_score": "INTEGER",
                "summary_pass": "INTEGER",
                "summary_reason": "TEXT"
            }
        }

        for table, columns_to_add in migrations.items():

            cursor.execute(f"PRAGMA table_info({table})")
            existing_columns = {
                row[1] for row in cursor.fetchall()
            }

            for column, data_type in columns_to_add.items():

                if column not in existing_columns:
                    cursor.execute(
                        f"ALTER TABLE {table} "
                        f"ADD COLUMN {column} {data_type}"
                    )

                    print(f"Added {table}.{column}")

        connection.commit()
        print("Database migration completed successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def repair_case_foreign_key():
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute("ALTER TABLE evaluation_cases RENAME TO evaluation_cases_old")
        cursor.execute("""
            CREATE TABLE evaluation_cases (
                run_id TEXT NOT NULL,
                test_case_id TEXT NOT NULL,
                expected_category TEXT,
                predicted_category TEXT,
                category_pass INTEGER,
                latency_seconds REAL,
                status TEXT NOT NULL,
                error TEXT,
                PRIMARY KEY (run_id, test_case_id),
                FOREIGN KEY (run_id)
                REFERENCES evaluation_runs(run_id)
                ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            INSERT INTO evaluation_cases (
                run_id,
                test_case_id,
                expected_category,
                predicted_category,
                category_pass,
                latency_seconds,
                status,
                error
            )
            SELECT
                run_id,
                test_case_id,
                expected_category,
                predicted_category,
                category_pass,
                latency_seconds,
                status,
                error
            FROM evaluation_cases_old
        """)
        cursor.execute("DROP TABLE evaluation_cases_old")
        connection.commit()
        cursor.execute("PRAGMA foreign_key_check")
        errors = cursor.fetchall()
        if errors:
            raise sqlite3.IntegrityError(f"Foreign-key violations: {errors}")
        print("Evaluation-case foreign key repaired.")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

if __name__ == "__main__":
    initialize_database()
    migrate_database()
    print("Database initialized and migrated successfully.")