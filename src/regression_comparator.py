
import argparse
import json

from .paths import REPORTS_DIR


def load_evaluation(filename):
    file_path = REPORTS_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_evaluation(evaluation, label):
    required_fields = [
        "prompt_version",
        "accuracy",
        "results"
    ]

    for field in required_fields:
        if field not in evaluation:
            raise ValueError(
                f"{label} evaluation is missing field: {field}"
            )

    results = evaluation["results"]

    if not isinstance(results, list) or not results:
        raise ValueError(
            f"{label} evaluation contains no valid results."
        )

    test_ids = []

    for result in results:
        if not isinstance(result, dict):
            raise ValueError(
                f"{label} contains an invalid result record."
            )

        required_result_fields = [
            "test_case_id",
            "category_pass",
            "status"
        ]

        for field in required_result_fields:
            if field not in result:
                raise ValueError(
                    f"{label} result is missing field: {field}"
                )

        test_id = result["test_case_id"]

        if not isinstance(test_id, str) or not test_id.strip():
            raise ValueError(
                f"{label} contains an invalid test case ID."
            )

        test_ids.append(test_id)

        if result["status"] != "success":
            raise ValueError(
                f"{label} evaluation failed for test case {test_id}."
            )

        if not isinstance(result["category_pass"], bool):
            raise ValueError(
                f"{label} has invalid category_pass for {test_id}."
            )

    if len(test_ids) != len(set(test_ids)):
        raise ValueError(
            f"{label} contains duplicate test case IDs."
        )

def compare_evaluations(baseline, candidate):
    validate_evaluation(baseline, "Baseline")
    validate_evaluation(candidate, "Candidate")
    
    baseline_results = {result["test_case_id"]: result for result in baseline["results"]}
    candidate_results = {result["test_case_id"]: result for result in candidate["results"]}

    baseline_ids = set(baseline_results)
    candidate_ids = set(candidate_results)

    common_ids = baseline_ids & candidate_ids

    missing_from_candidate = sorted(baseline_ids - candidate_ids)
    new_in_candidate = sorted(candidate_ids - baseline_ids)

    evaluation_valid = (
        len(missing_from_candidate) == 0
        and len(new_in_candidate) == 0
    )

    validation_errors = []

    if missing_from_candidate:
        validation_errors.append(
            f"Candidate is missing {len(missing_from_candidate)} "
            f"baseline test case(s): {missing_from_candidate}"
        )

    if new_in_candidate:
        validation_errors.append(
            f"Candidate contains {len(new_in_candidate)} "
            f"unexpected test case(s): {new_in_candidate}"
        )

    regressions = []
    improvements = []
    unchanged = []

    for test_id in sorted(common_ids):

        old = baseline_results[test_id]
        new = candidate_results[test_id]

        old_pass = old["category_pass"]
        new_pass = new["category_pass"]

        if old_pass is True and new_pass is False:
            regressions.append(test_id)

        elif old_pass is False and new_pass is True:
            improvements.append(test_id)

        elif old_pass == new_pass:
            unchanged.append(test_id)

    accuracy_delta = (
        candidate["accuracy"] - baseline["accuracy"]
        if baseline.get("accuracy") is not None
        and candidate.get("accuracy") is not None
        else None
    )

    summary_score_delta = (
        candidate["average_summary_score"]
        - baseline["average_summary_score"]
        if baseline.get("average_summary_score") is not None
        and candidate.get("average_summary_score") is not None
        else None
    )

    summary_pass_rate_delta = (
        candidate["summary_pass_rate"]
        - baseline["summary_pass_rate"]
        if baseline.get("summary_pass_rate") is not None
        and candidate.get("summary_pass_rate") is not None
        else None
    )

    category_severity = classify_regression_severity(accuracy_delta, warning_threshold=0.03, critical_threshold=0.08)
    summary_severity = classify_regression_severity(summary_pass_rate_delta, warning_threshold=0.03, critical_threshold=0.08)
    severity_levels = {
        "passed": 0,
        "warning": 1,
        "critical": 2,
        "insufficient_data": 3
    }

    severity = max([category_severity, summary_severity], key=lambda level: severity_levels[level])
    # Compare every category found in either evaluation.
    all_categories = (set(baseline.get("category_metrics", {})) | set(candidate.get("category_metrics", {})))
    category_comparison = {}

    for category in sorted(all_categories):

        old_accuracy = (baseline.get("category_metrics", {}).get(category, {}).get("accuracy"))
        new_accuracy = (candidate.get("category_metrics", {}).get(category, {}).get("accuracy"))
        category_comparison[category] = {
            "baseline_accuracy": old_accuracy,
            "candidate_accuracy": new_accuracy,
            "accuracy_delta": (
                new_accuracy - old_accuracy
                if old_accuracy is not None
                and new_accuracy is not None
                else None
            )
        }

    # Compare summary evaluation results.
    summary_regressions = []
    summary_improvements = []
    summary_unchanged = []

    for test_id in sorted(common_ids):

        old = baseline_results[test_id]
        new = candidate_results[test_id]

        old_pass = old.get("summary_pass")
        new_pass = new.get("summary_pass")

        if old_pass is True and new_pass is False:
            summary_regressions.append(test_id)

        elif old_pass is False and new_pass is True:
            summary_improvements.append(test_id)

        elif old_pass == new_pass:
            summary_unchanged.append(test_id)

    return {
        "baseline_version": baseline["prompt_version"],
        "candidate_version": candidate["prompt_version"],

        "baseline_accuracy": baseline["accuracy"],
        "candidate_accuracy": candidate["accuracy"],
        "accuracy_delta": accuracy_delta,

        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,

        "missing_from_candidate": missing_from_candidate,
        "new_in_candidate": new_in_candidate,
        "evaluation_valid": evaluation_valid,
        "validation_errors": validation_errors,

        "category_comparison": category_comparison,
        "severity": severity,
        "baseline_average_summary_score": baseline.get("average_summary_score"),
        "candidate_average_summary_score": candidate.get("average_summary_score"),
        "summary_score_delta": summary_score_delta,
        "baseline_summary_pass_rate": baseline.get("summary_pass_rate"),
        "candidate_summary_pass_rate": candidate.get("summary_pass_rate"),

        "summary_pass_rate_delta": summary_pass_rate_delta,

        "summary_regressions": summary_regressions,
        "summary_improvements": summary_improvements,
        "summary_unchanged": summary_unchanged,

        "summary_severity": summary_severity
    }


def classify_regression_severity(accuracy_delta, warning_threshold=0.03, critical_threshold=0.08):

    if warning_threshold < 0 or critical_threshold < 0:
        raise ValueError("Thresholds cannot be negative.")

    if critical_threshold <= warning_threshold:
        raise ValueError("Critical threshold must be greater than warning threshold.")

    if accuracy_delta is None:
        return "insufficient_data"

    degradation = max(0.0, -accuracy_delta)

    if degradation > critical_threshold:
        return "critical"

    if degradation > warning_threshold:
        return "warning"

    return "passed"


def main():

    parser = argparse.ArgumentParser(description="Compare two LLM evaluation runs.")
    parser.add_argument("--baseline", required=True, help="Baseline prompt version, for example v1.")

    parser.add_argument("--candidate", required=True, help="Candidate prompt version, for example v3.")
    args = parser.parse_args()

    baseline_filename = (f"evaluation_results_{args.baseline}.json")
    candidate_filename = (f"evaluation_results_{args.candidate}.json")

    baseline = load_evaluation(baseline_filename)
    candidate = load_evaluation(candidate_filename)

    # Prevent accidental comparison against mismatched files.
    if baseline["prompt_version"] != args.baseline:
        raise ValueError("Baseline version does not match requested version.")

    if candidate["prompt_version"] != args.candidate:
        raise ValueError("Candidate version does not match requested version.")

    comparison = compare_evaluations(baseline, candidate)

    print(json.dumps(comparison, indent=4))

    output_path = REPORTS_DIR / "regression_comparison.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(comparison, file, indent=4)

    print(f"\nComparison saved to {output_path}")
    print("\nComparison completed.")


if __name__ == "__main__":
    main()
