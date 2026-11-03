import os 
import json
from pathlib import Path
from dotenv import load_dotenv
from .paths import ENV_FILE, PROMPTS_DIR
from groq import Groq
import yaml
import time

load_dotenv(dotenv_path=ENV_FILE)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found. check .env file.")

client = Groq(api_key=api_key)

def load_prompt_config(path=None):

    if path is None:
        path = PROMPTS_DIR / "v1.yaml"
    else:
        path = Path(path)

        if not path.is_absolute():
            path = PROMPTS_DIR.parent / path

    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError("Prompt configuration must be a YAML dictionary.")

    if "version_id" not in config:
        raise ValueError("Missing version_id in prompt configuration.")

    if "system_prompt" not in config:
        raise ValueError("Missing system_prompt in prompt configuration.")

    return config

def classify_email(email: str, config: dict | None = None) -> dict:
    if not email or not email.strip():
        raise ValueError("Email cannot be empty.")

    # Load configuration only when it isn't supplied
    if config is None:
        config = load_prompt_config()

    # Measure API latency
    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": email}
        ],
        temperature=0
    )

    latency = time.perf_counter() - start_time

    # Extract raw model output
    raw_output = response.choices[0].message.content

    try:
        data = json.loads(raw_output)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(
            f"The model did not return valid JSON: {raw_output}"
        ) from exc

    allowed_categories = {
        "billing", "technical", "account", "general"
    }

    category = data.get("category")
    summary = data.get("summary")

    if category not in allowed_categories:
        raise ValueError(f"Invalid category returned: {category}")

    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("The model returned an invalid summary.")

    # Extract API usage metadata
    usage = response.usage

    return {
        "category": category,
        "summary": summary.strip(),
        "latency_seconds": latency,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "total_tokens": usage.total_tokens if usage else None,
        "raw_output": raw_output,
        "prompt_version": config["version_id"]
    }


if __name__ == "__main__":
    sample_email = (
        "Hello, I was charged twice for my monthly subscription. "
        "Could you please refund the extra payment?"
    )

    result = classify_email(sample_email)

    print("Input email:")
    print(sample_email)

    print("\nClassification result:")
    print(json.dumps(result, indent=4))
