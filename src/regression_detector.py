import json
import argparse

expected = ["positive", "negative", "positive", "negative", "positive",]
version_1 = ["positive", "negative", "positive", "negative", "positive",]
version_2 = ["positive", "positive", "negative", "negative", "positive",]

def evaluate_model(expected, predictions):
    if len(expected) != len(predictions):
        raise ValueError("Dataset lengths must match.")

    if not expected:
        raise ValueError("Dataset cannot be empty.")

    correct = sum(actual == predicted for actual, predicted in zip(expected, predictions))
    return correct / len(expected)

def generate_regression_report(expected, old_predictions, new_predictions, threshold = 0.05):
    old_accuracy = evaluate_model(expected=expected, predictions=old_predictions)
    new_accuracy = evaluate_model(expected=expected, predictions=new_predictions)
    
    epsilon = 1e-9
    drop = old_accuracy - new_accuracy
    regression_detected = drop > threshold + epsilon
    failed_cases = []
    for i, (actual, predicted) in enumerate(zip(expected, new_predictions), start=1):
        if actual != predicted:
            failed_cases.append({
                "test_case": i,
                "expected": actual,
                "predicted": predicted
            })

    print("\n------REGRESSION REPORT-------")
    print(f"Old Accuracy: {old_accuracy:.1%}")
    print(f"New Accuracy: {new_accuracy:.1%}")
    print(f"Performance Drop: {drop:.1%}")
    
    if regression_detected:
        print("Status: REGRESSION DETECTED")
    else:
        print("Status: NO REGRESSION DETECTED")
    
    print("\nFailed test cases")
    if failed_cases:
        for case in failed_cases:
            print(
                f"Case {case['test_case']}: "
                f"Expected={case['expected']}, "
                f"Predicted={case['predicted']}"
            )
    else:
        print("No failed test cases.")
    
    return {
        "old_accuracy": old_accuracy,
        "new_accuracy": new_accuracy,
        "drop": drop,
        "regression_detected": regression_detected,
        "failed_cases": failed_cases,
    }

def compare_versions(baseline_accuracy, versions, threshold=0.05):
    if not 0 <= baseline_accuracy <= 1:
        raise ValueError("Baseline accuracy must be between 0 and 1.")
    if not versions:
        raise ValueError("At least one model version must be provided.")
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1.")
    
    epsilon = 1e-9
    results = []
    for version, accuracy in versions.items():
        if not 0 <= accuracy <= 1:
            raise ValueError(f"Invalid accuracy for {version}: {accuracy}")
        drop = baseline_accuracy - accuracy
        results.append({
            "version": version,
            "accuracy": accuracy,
            "drop": drop,
            "regression": drop>threshold + epsilon
        })
    return results

def print_version_report(baseline_accuracy, versions, threshold=0.5):
    results = compare_versions(baseline_accuracy, versions, threshold)
    print("\n===== MODEL VERSION REPORT =====")
    print(f"Baseline accuracy: {baseline_accuracy:.1%}")
    print(f"Regression threshold: {threshold:.1%}")
    print("-" * 65)
    print(
        f"{'Version':<12}"
        f"{'Accuracy':<12}"
        f"{'Drop':<12}"
        f"{'Status'}"
    )
    print("-" * 65)
    for result in results:
        if result["drop"] > threshold:
            status = "REGRESSION"
        elif result["drop"] > 0:
            status = "BELOW BASELINE"
        else:
            status = "OK / IMPROVED"

        print(
            f"{result['version']:<12}"
            f"{result['accuracy']:.1%}        "
            f"{result['drop']:.1%}        "
            f"{status}"
        )

    return results

def save_results(results, filename="evaluation_results.json"):
    with open(filename, "w") as file:
        json.dump(results, file, indent=4)
    
    print(f"Results saved to {filename}")

def load_results(filename="evaluation_results.json"):
    try:
        with open(filename, "r") as file:
                results = json.load(file)
                return results
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    
    except json.JSONDecodeError:
        print(f"Invalid json in file: {filename}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Model Regression Detection System")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.06,
        help="Allowed accuracy drop (default: 0.05)"
    )
    parser.add_argument(
        "--baseline",
        type=float,
        default=0.92,
        help="Baseline model accuracy (default: 0.92)"
    )
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1:
        parser.error("Threshold must be between 0 and 1.")
    if not 0 <= args.baseline <= 1:
        parser.error("Baseline accuracy must be between 0 and 1.")
    
    return args

if __name__ == "__main__":
    args = parse_arguments()
    results = compare_versions(
            args.baseline,
            {"v1": 0.90, "v2": 0.85},
            threshold=args.threshold
            )
    print(results)
    # save_results(results)
    # invalid_results = load_results("invalid.json")
    # print(invalid_results)
    
    