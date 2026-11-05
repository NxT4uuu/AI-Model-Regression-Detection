import re
import time
from groq import APIConnectionError, APIStatusError, APITimeoutError

MAX_ATTEMPTS = 5
BASE_DELAY = 1
MAX_DELAY = 30

def get_retry_delay(error, attempt):
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", {}) or {}
    # Check server-provided retry information first.
    for header in ("retry-after", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"):
        value = headers.get(header)
        if value:
            match = re.match(
                r"^\s*(\d+(?:\.\d+)?)\s*(ms|s|m)?\s*$",
                str(value),
                re.IGNORECASE
            )

            if match:
                amount = float(match.group(1))
                unit = (match.group(2) or "s").lower()
                if unit == "ms":
                    return max(amount / 1000, 0.1)
                if unit == "m":
                    return amount * 60
                return max(amount, 0.1)
    # Exponential backoff when server timing is unavailable.
    return min(BASE_DELAY * (2 ** (attempt - 1)), MAX_DELAY)

def retry_api_call(operation, *args, **kwargs):
    """
    Retry transient Groq API failures.
    Retries:
    - HTTP 429: rate limit
    - HTTP 500, 502, 503, 504: temporary server failures
    - Connection errors and timeouts
    """
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return operation(*args, **kwargs)
        except (APIConnectionError, APITimeoutError, APIStatusError) as error:
            status_code = getattr(error, "status_code", None)
            retryable = (
                isinstance(error, (APIConnectionError, APITimeoutError))
                or status_code in (429, 500, 502, 503, 504)
            )
            if not retryable or attempt == MAX_ATTEMPTS:
                raise
            delay = get_retry_delay(error, attempt)
            print(
                f"Groq API request failed "
                f"(attempt {attempt}/{MAX_ATTEMPTS}, "
                f"status={status_code}). "
                f"Retrying in {delay:.2f} seconds..."
            )
            time.sleep(delay)

    raise RuntimeError("Groq API retry attempts exhausted.")
