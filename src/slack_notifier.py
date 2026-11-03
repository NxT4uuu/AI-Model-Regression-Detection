
import os
import requests

from dotenv import load_dotenv
from .paths import ENV_FILE

load_dotenv(dotenv_path=ENV_FILE)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_notification(comparison, deployment_decision):

    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL is not configured.")

    baseline_version = comparison["baseline_version"]
    candidate_version = comparison["candidate_version"]
    severity = comparison["severity"]

    accuracy = comparison["candidate_accuracy"]
    summary_score = comparison.get(
        "candidate_average_summary_score"
    )
    summary_pass_rate = comparison.get(
        "candidate_summary_pass_rate"
    )

    decision = deployment_decision["decision"]
    allowed = deployment_decision["deployment_allowed"]

    status_emoji = {
        "passed": ":white_check_mark:",
        "warning": ":warning:",
        "critical": ":rotating_light:",
        "insufficient_data": ":no_entry:"
    }

    message = {
        "text": f"AI Model Regression Alert: {severity.upper()}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "AI Model Regression Report"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Baseline Version:*\n{baseline_version}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Candidate Version:*\n{candidate_version}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{status_emoji.get(severity, '')} {severity.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Deployment Decision:*\n{decision}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Category Accuracy:*\n{accuracy:.2%}" if accuracy is not None else "*Category Accuracy:*\nN/A"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Average Summary Score:*\n{summary_score}/5" if summary_score is not None else "*Average Summary Score:*\nN/A"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Summary Pass Rate:*\n{summary_pass_rate:.2%}" if summary_pass_rate is not None else "*Summary Pass Rate:*\nN/A"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        ":lock: *Deployment allowed*"
                        if allowed
                        else ":no_entry: *Deployment blocked*"
                    )
                }
            }
        ]
    }

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json=message,
        timeout=15
    )

    response.raise_for_status()

    if response.text.strip() != "ok":
        raise RuntimeError(
            f"Slack rejected the notification: {response.text}"
        )

    print("Slack notification sent successfully.")
