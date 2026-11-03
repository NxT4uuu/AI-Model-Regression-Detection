import unittest
from src.deployment_gate import deployment_decision

class TestDeploymentGate(unittest.TestCase):

    def test_passed_severity(self):
        result = deployment_decision("passed")

        self.assertTrue(result["deployment_allowed"])
        self.assertEqual(result["decision"], "APPROVED")

    def test_warning_severity(self):
        result = deployment_decision("warning")

        self.assertTrue(result["deployment_allowed"])
        self.assertEqual(
            result["decision"],
            "APPROVED_WITH_WARNING"
        )

    def test_critical_severity(self):
        result = deployment_decision("critical")

        self.assertFalse(result["deployment_allowed"])
        self.assertEqual(result["decision"], "BLOCKED")

    def test_insufficient_data(self):
        result = deployment_decision("insufficient_data")

        self.assertFalse(result["deployment_allowed"])
        self.assertEqual(result["decision"], "BLOCKED")

    def test_unknown_severity(self):
        with self.assertRaises(ValueError):
            deployment_decision("unknown")

    def test_empty_severity(self):
        with self.assertRaises(ValueError):
            deployment_decision("")

    
    def test_invalid_evaluation_is_blocked(self):
        result = deployment_decision(
            "passed",
            evaluation_valid=False,
            validation_errors=["Missing test case"]
        )

        self.assertFalse(result["deployment_allowed"])
        self.assertEqual(result["decision"], "BLOCKED")


    def test_valid_evaluation_with_warning_is_approved(self):
        result = deployment_decision(
            "warning",
            evaluation_valid=True
        )

        self.assertTrue(result["deployment_allowed"])
        self.assertEqual(result["decision"], "APPROVED_WITH_WARNING")

    def test_invalid_evaluation_blocks_critical_candidate(self):
        result = deployment_decision(
            "critical",
            evaluation_valid=False
        )

        self.assertFalse(result["deployment_allowed"])
        self.assertEqual(result["decision"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
