import json
import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.pipeline import run_pipeline

# Simulates an existing candidate prompt file.
class ExistingPromptPath:
    def __truediv__(self, other):
        return self

    def is_file(self):
        return True

# Simulates a missing candidate prompt file.
class MissingPromptPath:
    def __truediv__(self, other):
        return self

    def is_file(self):
        return False
class TestPipeline(unittest.TestCase):

    @patch("src.pipeline.send_slack_notification")
    @patch("src.pipeline.deployment_decision")
    @patch("src.pipeline.run_command")
    @patch("src.pipeline.PROJECT_ROOT",new_callable=ExistingPromptPath)
    @patch("builtins.open", new_callable=mock_open)
    def test_approved_pipeline(
        self,
        mock_file,
        mock_project_root,
        mock_run_command,
        mock_deployment,
        mock_slack
    ):

        comparison = {"severity": "passed","baseline_version": "v1","candidate_version": "v2"}
        mock_file.return_value.read.return_value = json.dumps(comparison)
        decision = {
            "deployment_allowed": True,
            "decision": "APPROVED",
            "message": "Candidate passed regression evaluation."
        }

        mock_deployment.return_value = decision

        result = run_pipeline("v1", "v2")

        self.assertEqual(result, decision)
        self.assertEqual(mock_run_command.call_count, 3)

        mock_slack.assert_called_once_with(comparison,decision)

    @patch("src.pipeline.send_slack_notification")
    @patch("src.pipeline.deployment_decision")
    @patch("src.pipeline.run_command")
    @patch("src.pipeline.PROJECT_ROOT",new_callable=ExistingPromptPath)
    @patch("builtins.open", new_callable=mock_open)
    def test_blocked_pipeline_still_sends_slack(
        self,
        mock_file,
        mock_project_root,
        mock_run_command,
        mock_deployment,
        mock_slack
    ):

        comparison = {"severity": "critical","baseline_version": "v1","candidate_version": "v3"}
        mock_file.return_value.read.return_value = json.dumps(comparison)

        decision = {
            "deployment_allowed": False,
            "decision": "BLOCKED",
            "message": "Critical regression detected."
        }

        mock_deployment.return_value = decision

        result = run_pipeline("v1", "v3")

        self.assertFalse(result["deployment_allowed"])

        mock_slack.assert_called_once_with(comparison,decision)

    @patch("src.pipeline.run_command")
    @patch("src.pipeline.PROJECT_ROOT",new_callable=MissingPromptPath)
    def test_missing_prompt_stops_pipeline(self,mock_project_root,mock_run_command):
        with self.assertRaises(FileNotFoundError):
            run_pipeline("v1", "v99")
        mock_run_command.assert_not_called()
    @patch("src.pipeline.run_command")
    @patch("src.pipeline.PROJECT_ROOT",new_callable=ExistingPromptPath)
    
    def test_evaluation_failure_stops_pipeline(
        self,
        mock_project_root,
        mock_run_command
    ):

        mock_run_command.side_effect = RuntimeError("Pipeline command failed")
        with self.assertRaises(RuntimeError):
            run_pipeline("v1", "v2")

        # Only the first stage should have been attempted.
        self.assertEqual(mock_run_command.call_count, 1)

    @patch("src.pipeline.send_slack_notification")
    @patch("src.pipeline.deployment_decision")
    @patch("src.pipeline.run_command")
    @patch("src.pipeline.PROJECT_ROOT", new_callable=ExistingPromptPath)
    @patch("builtins.open", new_callable=mock_open)
    def test_slack_failure_does_not_stop_pipeline(
        self,
        mock_file,
        mock_project_root,
        mock_run_command,
        mock_deployment,
        mock_slack
    ):
        mock_file.return_value.read.return_value = json.dumps({
            "severity": "passed",
            "evaluation_valid": True,
            "validation_errors": []
        })

        mock_deployment.return_value = {
            "deployment_allowed": True,
            "decision": "APPROVED",
            "message": "Candidate passed regression evaluation."
        }

        mock_slack.side_effect = RuntimeError(
            "Slack notification failed"
        )

        decision = run_pipeline(
            baseline_version="v1",
            candidate_version="v2"
        )

        self.assertTrue(decision["deployment_allowed"])
        self.assertEqual(decision["decision"], "APPROVED")
        mock_slack.assert_called_once()    
    
if __name__ == "__main__":
    unittest.main()
