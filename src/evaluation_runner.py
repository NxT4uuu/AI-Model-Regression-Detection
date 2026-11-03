import json
import argparse
from datetime import datetime, timezone

from .dataset_loader import load_golden_dataset
from .email_classifier import load_prompt_config, classify_email
from .database import initialize_database, migrate_database, save_evaluation
from .paths import REPORTS_DIR, PROMPTS_DIR
from .summary_evaluator import evaluate_summary

def run_evaluation(prompt_path=None):

    dataset = load_golden_dataset()

    if prompt_path is None:
        config = load_prompt_config()
    else:
        config = load_prompt_config(prompt_path)

    results = []

    for item in dataset:
        test_id = item["id"]
        email = item["input"]
        expected = item["expected_output"]

        try:
            prediction = classify_email(email=email, config=config)

            category_pass = (
                prediction["category"] == expected["category"]
            )
            
            summary_evaluation = evaluate_summary(
                original_email=item["input"],
                expected_summary=item["expected_output"]["summary"],
                generated_summary=prediction["summary"]
            )

            summary_score = summary_evaluation["score"]
            summary_pass = summary_score >= 3
            results.append({
                "test_case_id": test_id,
                "expected_category": expected["category"],
                "predicted_category": prediction["category"],
                "expected_summary": expected["summary"],
                "predicted_summary": prediction["summary"],
                "category_pass": category_pass,
                "latency_seconds": prediction["latency_seconds"],
                "prompt_tokens": prediction["prompt_tokens"],
                "completion_tokens": prediction["completion_tokens"],
                "total_tokens": prediction["total_tokens"],
                "prompt_version": prediction["prompt_version"],
                "status": "success",
                "summary_score": summary_score,
                "summary_reason": summary_evaluation["reason"],
                "summary_pass": summary_pass,
                "error": None
            })

        except Exception as exc:
            results.append({
                "test_case_id": test_id,
                "expected_category": expected["category"],
                "predicted_category": None,
                "expected_summary": expected["summary"],
                "predicted_summary": None,
                "category_pass": None,
                "latency_seconds": None,
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
                "prompt_version": config["version_id"],
                "status": "error",
                "error": str(exc)
            })

    successful = [result for result in results if result["status"] == "success"]
    failures = [result for result in results if result["status"] == "error"]

    # Calculate per-category accuracy
    categories = ("billing", "technical", "account", "general")
    category_metrics = {}

    for category in categories:

        category_results = [result for result in successful if result["expected_category"] == category]
        category_total = len(category_results)
        category_correct = sum(result["category_pass"] for result in category_results)

        category_metrics[category] = {
            "total": category_total,
            "correct": category_correct,
            "accuracy": (category_correct / category_total if category_total else None)}

    total = len(results)
    successful_count = len(successful)

    correct = sum(result["category_pass"] for result in successful)
    accuracy = (correct / successful_count if successful_count else None)
    # Aggregate API metadata
    total_tokens = sum(result["total_tokens"] or 0 for result in successful)
    average_latency = (sum(result["latency_seconds"] for result in successful) / successful_count if successful_count else None)
    
    summary_scores = [
        result["summary_score"]
        for result in results
        if result.get("summary_score") is not None
    ]

    summary_passes = [
        result["summary_pass"]
        for result in results
        if result.get("summary_pass") is not None
    ]

    average_summary_score = (
        sum(summary_scores) / len(summary_scores)
        if summary_scores else None
    )

    summary_pass_rate = (
        sum(summary_passes) / len(summary_passes)
        if summary_passes else None
    )

    report = {
        "run_id": datetime.now(timezone.utc).isoformat(),
        "prompt_version": config["version_id"],
        "total_cases": total,
        "successful_cases": successful_count,
        "failed_cases": len(failures),
        "correct_predictions": correct,
        "accuracy": accuracy,
        "average_latency_seconds": average_latency,
        "total_tokens": total_tokens,
        "results": results,
        "category_metrics": category_metrics,
        "average_summary_score": average_summary_score,
        "summary_pass_rate": summary_pass_rate,
    }

    return report


def save_results(results, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    print(f"Results saved to {filename}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prompt",
        default=str(PROMPTS_DIR/"v1.yaml"),
        help="Path to the prompt configuration YAML file."
    )

    args = parser.parse_args()

    report = run_evaluation(args.prompt)
    # print(json.dumps(report, indent=4))
    initialize_database()
    migrate_database()
    save_evaluation(report)
    output_path = REPORTS_DIR / (f"evaluation_results_{report['prompt_version']}.json")

    save_results(report, output_path)

    print("\nEvaluation completed.")
