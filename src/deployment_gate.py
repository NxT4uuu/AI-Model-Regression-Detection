import json
import sys
from .paths import REPORTS_DIR

def deployment_decision(severity, evaluation_valid=True, validation_errors=None):
    if validation_errors is None:
        validation_errors = []

    if not isinstance(evaluation_valid, bool):
        raise ValueError("evaluation_valid must be a boolean.")

    if not evaluation_valid:
        return {
            "deployment_allowed": False,
            "decision": "BLOCKED",
            "message": "Invalid evaluation. Deployment blocked.",
            "validation_errors": validation_errors
        }

    decisions = {
        "passed": {
            "deployment_allowed": True,
            "decision": "APPROVED",
            "message": "Candidate passed regression evaluation."
        },
        "warning": {
            "deployment_allowed": True,
            "decision": "APPROVED_WITH_WARNING",
            "message": (
                "Performance degradation detected. "
                "Review recommended."
            )
        },
        "critical": {
            "deployment_allowed": False,
            "decision": "BLOCKED",
            "message": "Critical regression detected. Deployment blocked."
        },
        "insufficient_data": {
            "deployment_allowed": False,
            "decision": "BLOCKED",
            "message": "Insufficient evaluation data. Deployment blocked."
        }
    }

    if severity not in decisions:
        raise ValueError(f"Unknown severity: {severity}")

    result = decisions[severity].copy()
    result["validation_errors"] = []

    return result

def load_comparison():
    comparison_path = REPORTS_DIR / "regression_comparison.json"

    if not comparison_path.is_file():
        raise FileNotFoundError(
            f"Comparison report not found: {comparison_path}"
        )

    with open(comparison_path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    comparison = load_comparison()

    result = deployment_decision(
        severity=comparison.get("severity"),
        evaluation_valid=comparison.get("evaluation_valid", False),
        validation_errors=comparison.get("validation_errors", [])
    )

    print("\n--- DEPLOYMENT GATE ---")
    print(f"Baseline: {comparison['baseline_version']}")
    print(f"Candidate: {comparison['candidate_version']}")
    print(f"Severity: {comparison.get('severity')}")
    print(f"Evaluation valid: {comparison.get('evaluation_valid')}")
    print(f"Decision: {result['decision']}")
    print(f"Allowed: {result['deployment_allowed']}")
    print(f"Message: {result['message']}")

    for error in result["validation_errors"]:
        print(f"Validation error: {error}")

    if not result["deployment_allowed"]:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
