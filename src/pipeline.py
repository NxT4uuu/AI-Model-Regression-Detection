import argparse
import subprocess
import sys
import json

from .paths import PROJECT_ROOT, REPORTS_DIR
from .deployment_gate import deployment_decision
from .slack_notifier import send_slack_notification

def run_command(command):
    print(f"\nExecuting: {' '.join(command)}")

    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Pipeline command failed: {' '.join(command)}")

def run_pipeline(baseline_version="v1", candidate_version="v2"):
    candidate_prompt = f"prompts/{candidate_version}.yaml"
    python = sys.executable

    if not (PROJECT_ROOT / candidate_prompt).is_file():
        raise FileNotFoundError(f"Candidate prompt not found: {candidate_prompt}")
    
    print("\n------- AI REGRESSION PIPELINE -------")
    # Stage 1: Evaluate candidate prompt
    run_command([python,"-m","src.evaluation_runner","--prompt",candidate_prompt])
    # Stage 2: Compare baseline and candidate
    run_command([python,"-m", "src.regression_comparator","--baseline",baseline_version, "--candidate", candidate_version])
    # Stage 3: Generate HTML report
    run_command([
                python,
                "-m",
                "src.report_generator",
                "--baseline", baseline_version,
                "--candidate", candidate_version
            ] )
    # Stage 4: Load comparison results
    comparison_path = REPORTS_DIR / "regression_comparison.json"

    with open(comparison_path, "r", encoding="utf-8") as file:
        comparison = json.load(file)

    # Stage 5: Make deployment decision
    decision = deployment_decision(
            severity=comparison["severity"],
            evaluation_valid=comparison.get("evaluation_valid", False),
            validation_errors=comparison.get("validation_errors", [])
        )

    print("\n--- DEPLOYMENT DECISION ---")
    print(f"Decision: {decision['decision']}")
    print(f"Allowed: {decision['deployment_allowed']}")
    print(f"Message: {decision['message']}")

    # Stage 6: Send Slack notification
    send_slack_notification(comparison, decision)

    print("\n------- PIPELINE COMPLETED -------")

    return decision

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AI regression detection pipeline.")
    parser.add_argument("--baseline", default="v1", help="Baseline prompt version.")
    parser.add_argument("--candidate", default="v2",help="Candidate prompt version.")
    args = parser.parse_args()
    try:
        decision = run_pipeline(baseline_version=args.baseline, candidate_version=args.candidate)
        if not decision["deployment_allowed"]:
            sys.exit(1)

    except Exception as error:
        print(f"\nPIPELINE ERROR: {error}")
        sys.exit(2)