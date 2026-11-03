
from pathlib import Path

# Root directory of Project_1
PROJECT_ROOT = Path(__file__).resolve().parent.parent

SRC_DIR = PROJECT_ROOT / "src"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATABASE_DIR = PROJECT_ROOT / "database"
TESTS_DIR = PROJECT_ROOT / "tests"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

GOLDEN_DATASET = DATA_DIR / "golden_dataset.json"
DATABASE_PATH = DATABASE_DIR / "evaluation_history.db"
ENV_FILE = PROJECT_ROOT / ".env"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
