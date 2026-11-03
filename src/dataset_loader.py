import json
from pathlib import Path
from .paths import GOLDEN_DATASET

VALID_CATEGORIES = {"billing", "technical", "account", "general"}

def load_golden_dataset(path=GOLDEN_DATASET):
    dataset_path = Path(path)
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"Golden dataset not found: {dataset_path}")
    
    with dataset_path.open("r",encoding="utf-8") as file:
        data = json.load(file)
        
    if not isinstance(data, list) or not data:
        raise ValueError("Golden dataset must be a non-empty JSON list.")
        
    seen_ids = set()

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Record {index} must be a JSON object.")

        required_fields = {
            "id",
            "input",
            "expected_output",
            "expected_difficulty",
            "notes"
        }

        missing = required_fields - item.keys()

        if missing:
            raise ValueError(
                f"Record {index} is missing fields: "
                f"{sorted(missing)}"
            )

        if not isinstance(item["id"], str) or not item["id"].strip():
            raise ValueError(f"Record {index} has an invalid ID.")

        if item["id"] in seen_ids:
            raise ValueError(f"Duplicate ID: {item['id']}")

        seen_ids.add(item["id"])

        if not isinstance(item["input"], str) or not item["input"].strip():
            raise ValueError(
                f"Record {item['id']} has an empty input."
            )

        expected = item["expected_output"]

        if not isinstance(expected, dict):
            raise ValueError(
                f"Record {item['id']} has an invalid expected_output."
            )

        category = expected.get("category")
        summary = expected.get("summary")

        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Record {item['id']} has an invalid category: "
                f"{category}"
            )

        if not isinstance(summary, str) or not summary.strip():
            raise ValueError(
                f"Record {item['id']} has an invalid expected summary."
            )

    return data

if __name__ == "__main__":
    dataset = load_golden_dataset()

    print("Golden dataset loaded successfully.")
    print(f"Number of records: {len(dataset)}")

    for item in dataset:
        print(
            f"{item['id']}: "
            f"expected category = "
            f"{item['expected_output']['category']}"
        )
