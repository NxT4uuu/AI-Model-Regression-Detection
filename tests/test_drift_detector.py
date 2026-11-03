
import unittest

from src.drift_detector import (
    calculate_moving_average,
    detect_performance_drift
)


def create_history(accuracies):

    return [
        (f"run_{index}", "v1", accuracy)
        for index, accuracy in enumerate(accuracies, start=1)
    ]


class TestDriftDetector(unittest.TestCase):

    def test_moving_average(self):

        history = create_history([1.0, 0.8, 0.9])

        result = calculate_moving_average(history, window=2)

        self.assertIsNone(result[0])
        self.assertAlmostEqual(result[1], 0.9)
        self.assertAlmostEqual(result[2], 0.85)

    def test_insufficient_history(self):

        history = create_history([1.0, 0.9, 0.8])

        result = detect_performance_drift(
            history,
            window=2
        )

        self.assertFalse(result["drift_detected"])
        self.assertEqual(result["status"], "insufficient_history")

    def test_drift_detected(self):

        history = create_history(
            [1.0] * 7 + [0.8] * 7
        )

        result = detect_performance_drift(
            history,
            window=7,
            threshold=0.05
        )

        self.assertTrue(result["drift_detected"])
        self.assertEqual(result["status"], "drift_detected")
        self.assertAlmostEqual(result["degradation"], 0.2)

    def test_stable_performance(self):

        history = create_history([0.9] * 14)

        result = detect_performance_drift(
            history,
            window=7,
            threshold=0.05
        )

        self.assertFalse(result["drift_detected"])
        self.assertEqual(result["status"], "stable")

    def test_small_degradation_below_threshold(self):

        history = create_history(
            [0.95] * 7 + [0.92] * 7
        )

        result = detect_performance_drift(
            history,
            window=7,
            threshold=0.05
        )

        self.assertFalse(result["drift_detected"])

    def test_invalid_window(self):

        history = create_history([0.9] * 14)

        with self.assertRaises(ValueError):
            calculate_moving_average(history, window=0)

    def test_invalid_threshold(self):

        history = create_history([0.9] * 14)

        with self.assertRaises(ValueError):
            detect_performance_drift(
                history,
                window=7,
                threshold=-0.05
            )

    def test_invalid_accuracy(self):

        history = create_history([0.9, 1.5, 0.8])

        with self.assertRaises(ValueError):
            calculate_moving_average(history, window=2)


if __name__ == "__main__":
    unittest.main()
