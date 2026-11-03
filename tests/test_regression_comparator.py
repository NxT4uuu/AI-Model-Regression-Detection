import unittest
from src.regression_comparator import (compare_evaluations, classify_regression_severity)

def create_evaluation(version, accuracy, category_pass, summary_pass=None):
    if summary_pass is None:
        summary_pass = [True] * len(category_pass)

    if len(category_pass) != len(summary_pass):
        raise ValueError(
            "category_pass and summary_pass must have equal lengths."
        )

    results = []

    for index, (category, summary) in enumerate(
        zip(category_pass, summary_pass), start=1
    ):
        results.append({
            "test_case_id": f"email_{index:03d}",
            "category_pass": category,
            "summary_pass": summary,
            "status": "success"
        })

    return {
        "prompt_version": version,
        "accuracy": accuracy,
        "average_summary_score": 5.0,
        "summary_pass_rate": (
            sum(summary_pass) / len(summary_pass)
            if summary_pass else None
        ),
        "category_metrics": {
            "billing": {
                "accuracy": accuracy
            }
        },
        "results": results
    }


class TestRegressionComparator(unittest.TestCase):

    def test_no_regression(self):
        baseline = create_evaluation("v1", 1.0, [True, True, True])
        candidate = create_evaluation("v2", 1.0, [True, True, True])

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(result["severity"], "passed")
        self.assertEqual(result["regressions"], [])

    def test_critical_regression(self):
        baseline = create_evaluation("v1", 1.0, [True] * 10)
        candidate = create_evaluation(
            "v2", 0.6, [True] * 6 + [False] * 4
        )

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(result["severity"], "critical")
        self.assertEqual(len(result["regressions"]), 4)

    def test_warning_regression(self):
        baseline = create_evaluation("v1", 1.0, [True] * 100)
        candidate = create_evaluation(
            "v2", 0.96, [True] * 96 + [False] * 4
        )

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(result["severity"], "warning")

    def test_regression_identification(self):
        baseline = create_evaluation("v1", 1.0, [True, True, True])
        candidate = create_evaluation(
            "v2", 2 / 3, [True, False, True]
        )

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(result["regressions"], ["email_002"])

    def test_improvement_identification(self):
        baseline = create_evaluation(
            "v1", 2 / 3, [True, False, True]
        )
        candidate = create_evaluation("v2", 1.0, [True, True, True])

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(result["improvements"], ["email_002"])

    def test_summary_regression(self):
        baseline = create_evaluation(
            "v1", 1.0, [True, True], [True, True]
        )
        candidate = create_evaluation(
            "v2", 1.0, [True, True], [True, False]
        )

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(
            result["summary_regressions"], ["email_002"]
        )
        self.assertEqual(result["summary_severity"], "critical")

    def test_missing_test_case(self):
        baseline = create_evaluation(
            "v1", 1.0, [True, True, True]
        )
        candidate = create_evaluation(
            "v2", 1.0, [True, True]
        )

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(
            result["missing_from_candidate"], ["email_003"]
        )

    def test_improvement_does_not_create_regression(self):
        baseline = create_evaluation(
            "v1", 0.8, [True, True, False, False, True]
        )
        candidate = create_evaluation(
            "v2", 1.0, [True, True, True, True, True]
        )

        result = compare_evaluations(baseline, candidate)

        self.assertEqual(result["severity"], "passed")
        self.assertEqual(len(result["improvements"]), 2)

    def test_invalid_thresholds(self):
        with self.assertRaises(ValueError):
            classify_regression_severity(
                -0.1,
                warning_threshold=0.08,
                critical_threshold=0.03
            )

    def test_negative_threshold(self):
        with self.assertRaises(ValueError):
            classify_regression_severity(
                -0.1,
                warning_threshold=-0.03
            )

    def test_insufficient_data(self):
        result = classify_regression_severity(None)

        self.assertEqual(result, "insufficient_data")

    def test_failed_evaluation_record(self):
        baseline = create_evaluation("v1", 1.0, [True])
        candidate = create_evaluation("v2", 1.0, [True])

        candidate["results"][0]["status"] = "error"

        with self.assertRaises(ValueError):
            compare_evaluations(baseline, candidate)

    def test_missing_status_field(self):
        baseline = create_evaluation("v1", 1.0, [True])
        candidate = create_evaluation("v2", 1.0, [True])

        del candidate["results"][0]["status"]

        with self.assertRaises(ValueError):
            compare_evaluations(baseline, candidate)

    def test_duplicate_test_case_ids(self):
        baseline = create_evaluation("v1", 1.0, [True, True])
        candidate = create_evaluation("v2", 1.0, [True, True])

        candidate["results"][1]["test_case_id"] = "email_001"

        with self.assertRaises(ValueError):
            compare_evaluations(baseline, candidate)

    def test_missing_required_evaluation_field(self):
        baseline = create_evaluation("v1", 1.0, [True])
        candidate = create_evaluation("v2", 1.0, [True])

        del candidate["accuracy"]

        with self.assertRaises(ValueError):
            compare_evaluations(baseline, candidate)


if __name__ == "__main__":
    unittest.main()
