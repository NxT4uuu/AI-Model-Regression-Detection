import argparse
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .paths import REPORTS_DIR, PROJECT_ROOT

def load_json_report(filename):
    file_path = REPORTS_DIR / filename

    if not file_path.is_file():
        raise FileNotFoundError(f"Report file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def load_report_data(baseline_version="v1", candidate_version="v2"):
    if baseline_version == candidate_version:
        raise ValueError("Baseline and candidate versions must be different.")

    comparison = load_json_report("regression_comparison.json")
    baseline = load_json_report(f"evaluation_results_{baseline_version}.json")
    candidate = load_json_report(f"evaluation_results_{candidate_version}.json")
    # Prevent the report from combining unrelated evaluation runs.
    if baseline.get("prompt_version") != baseline_version:
        raise ValueError("Baseline evaluation version does not match the requested version.")

    if candidate.get("prompt_version") != candidate_version:
        raise ValueError("Candidate evaluation version does not match the requested version.")

    return {
        "comparison": comparison,
        "baseline": baseline,
        "candidate": candidate,
    }

def generate_html_report(data):
    template_dir = PROJECT_ROOT / "templates"
    environment = Environment(loader=FileSystemLoader(template_dir),autoescape=select_autoescape(["html", "xml"]))

    template = environment.get_template("regression_report.html")
    return template.render(**data)

def save_html_report(html_content):
    output_path = REPORTS_DIR / "regression_report.html"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"HTML report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate an AI model regression HTML report.")

    parser.add_argument("--baseline", default="v1")
    parser.add_argument("--candidate", default="v2")

    args = parser.parse_args()
    data = load_report_data(baseline_version=args.baseline, candidate_version=args.candidate)
    
    html_content = generate_html_report(data)
    save_html_report(html_content)
    print(f"Report generated for {args.baseline} → {args.candidate}.")

if __name__ == "__main__":
    main()
