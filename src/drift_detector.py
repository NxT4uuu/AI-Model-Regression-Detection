import sqlite3
import math
from .paths import DATABASE_PATH

DB_PATH = str(DATABASE_PATH)

def validate_history(history):
    # Validate evaluation history records

    if not isinstance(history, (list, tuple)):
        raise ValueError("History must be a list or tuple.")

    for row in history:
        if len(row) < 3:
            raise ValueError("Each history record must contain three fields.")

        accuracy = row[2]

        if (
            isinstance(accuracy, bool)
            or not isinstance(accuracy, (int, float))
            or not math.isfinite(accuracy)
            or not 0 <= accuracy <= 1
        ):
            raise ValueError("Accuracy must be a finite number between 0 and 1.")

def get_accuracy_history(prompt_version=None):
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        if prompt_version:
            cursor.execute("""
                SELECT run_id, prompt_version, accuracy
                FROM evaluation_runs
                WHERE prompt_version = ?
                  AND accuracy IS NOT NULL
                ORDER BY created_at ASC
            """, (prompt_version,))

        else:
            cursor.execute("""
                SELECT run_id, prompt_version, accuracy
                FROM evaluation_runs
                WHERE accuracy IS NOT NULL
                ORDER BY created_at ASC
            """)

        history = cursor.fetchall()
        validate_history(history)
        return history

    finally:
        connection.close()

def calculate_moving_average(history, window=7):
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0:
        raise ValueError("Window must be a positive integer.")

    validate_history(history)

    moving_averages = []

    for index in range(len(history)):
        if index + 1 < window:
            moving_averages.append(None)
            continue

        recent_runs = history[index - window + 1:index + 1]
        average = sum(row[2] for row in recent_runs) / window
        moving_averages.append(average)

    return moving_averages


def detect_performance_drift(history, window=7, threshold=0.05):

    if not isinstance(window, int) or isinstance(window, bool) or window <= 0:
        raise ValueError("Window must be a positive integer.")

    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or threshold < 0
    ):
        raise ValueError("Threshold must be a finite non-negative number.")

    validate_history(history)

    if len(history) < window * 2:

        return {
            "drift_detected": False,
            "status": "insufficient_history",
            "message": (
                f"At least {window * 2} runs are required "
                "to compare two complete windows."
            )
        }

    previous_window = history[-(window * 2):-window]
    recent_window = history[-window:]
    previous_average = (sum(row[2] for row in previous_window) / window)
    recent_average = (sum(row[2] for row in recent_window) / window)

    degradation = previous_average - recent_average
    drift_detected = degradation > threshold

    return {
        "drift_detected": drift_detected,
        "status": (
            "drift_detected"
            if drift_detected
            else "stable"
        ),
        "previous_average": previous_average,
        "recent_average": recent_average,
        "degradation": degradation,
        "threshold": threshold
    }

def main():
    # Monitor one prompt version at a time.
    history = get_accuracy_history(prompt_version="v2")

    if not history:
        print("No evaluation history found for v2.")
        return

    moving_averages = calculate_moving_average(history,window=7)
    print("\n--- EVALUATION PERFORMANCE HISTORY ---")

    for run, average in zip(history, moving_averages):
        run_id, version, accuracy = run

        print(f"\nRun ID: {run_id}")
        print(f"Prompt version: {version}")
        print(f"Accuracy: {accuracy:.2%}")

        if average is not None:
            print(f"7-run moving average: {average:.2%}")
        else:
            print("7-run moving average: Insufficient history")

    drift_report = detect_performance_drift(history,window=7,threshold=0.05)
    print("\n--- DRIFT DETECTION REPORT ---")

    for key, value in drift_report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
