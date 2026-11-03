# AI Model Regression Detection System

An automated evaluation and regression detection pipeline for Large Language Model (LLM)-powered applications. The system evaluates versioned prompts against a golden dataset, measures output quality, identifies performance regressions, generates comparison reports, and makes deployment decisions.

## 1. Project Overview

The AI Model Regression Detection System is a Python-based project designed to detect performance degradation in LLM-powered applications when prompts or model configurations change.

The project implements an email classification system as its evaluation target. It compares a baseline prompt version against a candidate version using a labelled golden dataset.

The evaluation pipeline measures:
- Classification accuracy.
- Generated summary quality using an LLM-as-a-Judge.
- Summary pass rate.
- Individual test-case regressions and improvements.
- Per-category performance changes.

Based on these results, the system determines whether a candidate prompt should be approved or blocked.

The project also includes historical evaluation storage, performance drift detection, HTML report generation, and Slack notifications.

## 2. Key Features

- **LLM-Based Email Classification:** Classifies customer support emails into Billing, Technical, Account, and General categories.
- **Prompt Version Management:** Maintains multiple prompt configurations using YAML files.
- **Golden Dataset:** Evaluates prompt versions against 50 labelled test cases.
- **Automated Evaluation:** Measures classification accuracy, execution latency, token usage, and summary quality.
- **LLM-as-a-Judge:** Evaluates generated summaries using a structured five-point scoring rubric.
- **Regression Detection:** Compares baseline and candidate evaluation results to identify regressions and improvements.
- **Category-Level Analysis:** Measures performance changes across individual email categories.
- **Evaluation Validation:** Checks test-case consistency, duplicate IDs, missing records, and failed evaluations.
- **Performance Drift Detection:** Uses historical evaluation results and moving averages to identify potential performance degradation.
- **SQLite Database:** Stores historical evaluation runs.
- **HTML Regression Reports:** Generates comparison reports with performance metrics and visualizations.
- **Slack Integration:** Sends automated notifications containing evaluation and deployment decisions.
- **Deployment Gate:** Approves or blocks candidate versions based on regression severity and evaluation validity.
- **Pipeline Orchestration:** Integrates evaluation, comparison, reporting, deployment decisions, and notifications into one execution workflow.
- **Automated Unit Testing:** Uses Python's `unittest` framework to test core components.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3 |
| LLM API | Groq API |
| LLM Model | `openai/gpt-oss-20b` |
| Prompt Configuration | YAML |
| Dataset Storage | JSON |
| Evaluation Database | SQLite |
| Summary Evaluation | LLM-as-a-Judge |
| HTML Report Generation | Jinja2 |
| Report Visualization | Chart.js |
| Notifications | Slack Incoming Webhooks |
| Testing | Python unittest |
| Environment Configuration | python-dotenv |

## 4. Project Structure

```text
Project_1/
│
├── data/
│   └── golden_dataset.json
│
├── database/
│   └── evaluation_history.db
│
├── prompts/
│   ├── v1.yaml
│   ├── v2.yaml
│   └── v3.yaml
│
├── reports/
│   ├── evaluation_results_v1.json
│   ├── evaluation_results_v2.json
│   ├── evaluation_results_v3.json
│   ├── regression_comparison.json
│   └── regression_report.html
│
├── scripts/
│   ├── check_db.py
│   ├── repair_db.py
│   ├── test_slack.py
│   └── verify_schema.py
│
├── src/
│   ├── email_classifier.py
│   ├── dataset_loader.py
│   ├── evaluation_runner.py
│   ├── summary_evaluator.py
│   ├── regression_detector.py
│   ├── regression_comparator.py
│   ├── drift_detector.py
│   ├── database.py
│   ├── deployment_gate.py
│   ├── report_generator.py
│   ├── slack_notifier.py
│   ├── pipeline.py
│   └── paths.py
│
├── static/
│   ├── css/
│   │   └── report_style.css
│   └── js/
│       └── performance_chart.js
│
├── templates/
│   └── regression_report.html
│
├── tests/
│   ├── test_deployment_gate.py
│   ├── test_drift_detector.py
│   ├── test_pipeline.py
│   └── test_regression_comparator.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 5. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- pip.
- A Groq API key.
- A Slack Incoming Webhook URL for notifications.

### Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI-Model-Regression-Detection
```

### Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv env1
.\env1\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

Replace the placeholder values with your actual credentials.

**Security:** Never commit `.env` or expose API keys and webhook URLs in source code or public repositories.

## 6. Golden Dataset

The project uses a JSON-based golden dataset containing 50 labelled customer support email examples.

Each test case includes:
- Unique test-case ID.
- Original email input.
- Expected classification category.
- Expected summary.
- Expected difficulty.
- Additional evaluation notes.

The four classification categories are:

1. Billing
2. Technical
3. Account
4. General

Validate the dataset using:

```powershell
python -m src.dataset_loader
```

## 7. Run the Evaluation

Evaluate a prompt version against the golden dataset:

```powershell
python -m src.evaluation_runner --prompt prompts/v1.yaml
```

For other versions:

```powershell
python -m src.evaluation_runner --prompt prompts/v2.yaml

python -m src.evaluation_runner --prompt prompts/v3.yaml
```

The evaluation runner:
- Loads the golden dataset.
- Loads the selected prompt configuration.
- Executes email classification.
- Evaluates generated summaries.
- Calculates performance metrics.
- Saves evaluation results as JSON.
- Stores evaluation history in SQLite.

## 8. Compare Prompt Versions

Compare a baseline prompt against a candidate prompt:

```powershell
python -m src.regression_comparator --baseline v1 --candidate v2
```

Example comparison:

```powershell
python -m src.regression_comparator --baseline v1 --candidate v3
```

The comparator identifies:
- Classification regressions.
- Classification improvements.
- Unchanged test cases.
- Per-category accuracy changes.
- Summary quality changes.
- Missing or unexpected test cases.
- Evaluation validity.
- Overall regression severity.

## 9. Generate HTML Regression Reports

Generate a comparison report:

```powershell
python -m src.report_generator --baseline v1 --candidate v3
```

The generated report is saved at:

```text
reports/regression_report.html
```

The report presents baseline and candidate performance metrics, regression details, summary evaluation results, and visual comparisons.

## 10. Deployment Gate

The deployment gate evaluates whether a candidate version should be approved or blocked.

Run:

```powershell
python -m src.deployment_gate
```

The decision depends on:
- Regression severity.
- Evaluation validity.
- Missing or invalid evaluation records.

Possible decisions include:

| Decision | Meaning |
|---|---|
| APPROVED | Candidate passes regression evaluation. |
| APPROVED_WITH_WARNING | Candidate is approved with a performance warning. |
| BLOCKED | Candidate fails the deployment criteria. |

## 11. Run the Complete Pipeline

The pipeline orchestrates the major project components.

Run:

```powershell
python -m src.pipeline --baseline v1 --candidate v3
```

The pipeline executes the following sequence:

1. Evaluate the candidate prompt.
2. Compare candidate and baseline results.
3. Generate the HTML regression report.
4. Apply the deployment gate.
5. Send a Slack notification.
6. Display the final pipeline status.

A candidate that fails the deployment criteria is blocked.

## 12. Performance Drift Detection

The drift detector uses historical evaluation results stored in SQLite.

It calculates moving averages and compares recent performance against previous evaluation windows to identify potential degradation.

The current implementation uses a seven-run window and requires sufficient historical evaluation data before detecting drift.

## 13. Run Unit Tests

Execute the test suite:

```powershell
python -m unittest discover -s tests -v
```

The tests cover regression comparison, deployment decisions, performance drift detection, and pipeline orchestration.

## 14. Limitations

- The current implementation uses an email classification task as its evaluation target.
- The golden dataset contains 50 test cases and requires further expansion and manual validation.
- LLM outputs are nondeterministic and may vary between evaluation runs.
- Summary quality is evaluated using an LLM-as-a-Judge and may be affected by judge-model bias.
- Evaluation results depend on API availability, model behaviour, and network conditions.
- Performance drift detection requires sufficient comparable historical evaluation runs.
- The current implementation does not establish production-level reliability from the available benchmark results.

## 15. Future Improvements

- Integrate GitHub Actions for automated CI/CD execution.
- Implement Docker-based deployment and reproducible environments.
- Expand and improve the golden dataset.
- Introduce dataset fingerprinting and evaluation reproducibility checks.
- Add repeated evaluations to measure LLM output variability.
- Improve drift detection for gradual performance changes.
- Add more evaluation metrics and configurable quality thresholds.
- Improve automated regression testing with deterministic synthetic test cases.
- Support additional LLM-powered applications beyond email classification.

## 16. Learning Outcomes

This project demonstrates practical implementation of LLM evaluation pipelines, prompt versioning, automated quality assessment, regression detection, LLM-as-a-Judge, performance monitoring, database integration, HTML reporting, API integration, deployment gating, and software testing.

It explores how changes in prompts and model configurations can be evaluated systematically before being accepted into an application workflow.