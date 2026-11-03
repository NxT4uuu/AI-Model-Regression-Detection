
# Model Regression Detection System

## 1. Project Overview

The Model Regression Detection System is a Python-based project designed to identify performance degradation between a baseline machine-learning model and a newer model.

It compares model accuracy, measures the performance drop, identifies misclassified samples, and reports whether the drop exceeds a configurable threshold.

The project also demonstrates regression detection using machine-learning models built with scikit-learn.

## 2. Features

- Calculate classification accuracy.
- Compare old and new model predictions.
- Detect performance regression using a configurable threshold.
- Compare multiple model versions against a baseline.
- Validate accuracy values, thresholds, and input datasets.
- Generate reports containing performance metrics and failed cases.
- Save and load evaluation results using JSON.
- Handle missing files and malformed JSON.
- Accept baseline accuracy and threshold values through command-line arguments.
- Run automated unit tests using Python's `unittest` framework.
- Demonstrate regression detection with scikit-learn decision trees.

## 3. Project Structure

```text
Project_1/
├── regression_detector.py
├── test_regression_detector.py
├── ml_model_demo.py
├── evaluation_results.json
└── README.md
```

## 4. Requirements

- Python 3
- scikit-learn
- Python standard-library modules, including `json`, `argparse`, and `unittest`

## 5. Setup

Activate the project's virtual environment.

On Windows PowerShell:

```powershell
.\env1\Scripts\Activate.ps1
```

If the virtual environment is located elsewhere, use its actual path.

Check the scikit-learn installation:

```powershell
python -c "import sklearn; print(sklearn.__version__)"
```

## 6. Run the Regression Detector

Run the main program with its default configuration:

```powershell
python regression_detector.py
```

Specify a custom baseline accuracy and threshold:

```powershell
python regression_detector.py --baseline 0.95 --threshold 0.05
```

Accuracy and threshold values are expressed as fractions between 0 and 1.

## 7. Run the Machine-Learning Demonstration

```powershell
python ml_model_demo.py
```

The demonstration trains decision-tree classifiers on the Iris dataset, compares their predictions, and reports changes in classification accuracy.

It also evaluates tree depths of 1, 2, and 3 to illustrate how model configuration affects performance on the selected train/test split.

## 8. Run Unit Tests

```powershell
python -m unittest -v
```

The project currently has 12 unit tests covering accuracy calculation, regression detection, input validation, multiple-version comparison, and boundary conditions.

The latest recorded test run passed all 12 tests.

## 9. Example Results

In the demonstrated Iris experiment:

| Model configuration    | Test accuracy |
| ---------------------- | ------------: |
| Decision tree, depth 1 |         63.3% |
| Decision tree, depth 2 |         96.7% |
| Decision tree, depth 3 |        100.0% |

With a baseline accuracy of 100% and a threshold of 5 percentage points, the depth-1 model triggered regression detection, while the depth-2 and depth-3 models did not.

These results are specific to the experiment's selected train/test split and random seed; they are not a guarantee of performance on other datasets.

## 10. Limitations

- Accuracy is the primary evaluation metric in the current implementation.
- The Iris experiment uses a single train/test split.
- The demonstration uses a small, built-in dataset.
- The current CLI uses predefined model versions rather than loading arbitrary trained models from user-supplied files.

## 11. Future Improvements

- Add support for precision, recall, F1-score, and other metrics.
- Add cross-validation and repeated evaluation.
- Store historical evaluation runs with timestamps.
- Add automated tests for JSON persistence.
- Support configurable datasets and trained model artifacts.
- Integrate the detector into a continuous integration pipeline.

## 12. Learning Outcomes

This project demonstrates Python programming, input validation, exception handling, unit testing, JSON persistence, command-line interfaces, classification metrics, and basic machine-learning model evaluation.
