from src.regression_comparator import load_evaluation, compare_evaluations
from src.deployment_gate import deployment_decision
from src.report_generator import load_report_data
from src.slack_notifier import send_slack_notification
data = load_report_data()

comparison = data["comparison"]

decision = deployment_decision(comparison["severity"])

print("Deployment decision:", decision)
print("Decision type:", type(decision))
send_slack_notification(comparison, decision)