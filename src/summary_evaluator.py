import json
from .email_classifier import client

SUMMARY_JUDGE_PROMPT = """
You are an impartial evaluator assessing the relevance and accuracy
of an AI-generated customer support email summary.

Evaluate the generated summary using:
1. The original customer email.
2. The expected reference summary.
3. The generated summary.

Scoring rubric:
5 - Accurately captures all essential information.
4 - Captures the main information with minor omissions.
3 - Partially relevant but misses important details.
2 - Contains major omissions or misleading information.
1 - Irrelevant or substantially factually incorrect.

Evaluation rules:
- Do not require identical wording.
- Evaluate meaning, not writing style.
- Penalize invented facts.
- Penalize important omissions.
- Ensure the generated summary is consistent with the original email.
- Do not reward a fluent summary if its information is inaccurate.

Return strictly valid JSON in this format:
{
    "score": 1,
    "reason": "Brief explanation of the score."
}

The score must be an integer between 1 and 5.
Do not include Markdown formatting or additional text.
"""

def evaluate_summary(original_email, expected_summary, generated_summary):
    if not original_email.strip():
        raise ValueError("Original email cannot be empty.")
    if not expected_summary.strip():
        raise ValueError("Expected summary cannot be empty.")
    if not generated_summary.strip():
        raise ValueError("Generated summary cannot be empty.")
    
    user_message = f"""
                    ORIGINAL CUSTOMER EMAIL:
                    {original_email}

                    EXPECTED SUMMARY:
                    {expected_summary}

                    GENERATED SUMMARY:
                    {generated_summary}

                    Evaluate the generated summary.
                """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": SUMMARY_JUDGE_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    raw_output = response.choices[0].message.content
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"judge returned invalid JSON: {raw_output}") from exc
    
    score = result.get("score")
    reason = result.get("reason")
    
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        raise ValueError(f"Invalid relevance score: {score}")
    
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Judge did not provide a valid explanation.")
    
    return {
        "score": score,
        "reason": reason.strip(),
        "raw_output": raw_output
    }