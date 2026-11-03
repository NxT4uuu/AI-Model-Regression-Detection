from .summary_evaluator import evaluate_summary

original_email = """
            I was charged twice for my monthly subscription.
            Please refund the duplicate payment.
            """

expected_summary = (
    "Customer reports a duplicate subscription charge "
    "and requests a refund."
)

generated_summary = (
    "Customer wants to upgrade their subscription plan."
)

result = evaluate_summary(
    original_email,
    expected_summary,
    generated_summary
)

print(result)