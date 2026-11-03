import unittest
from unittest.mock import patch, Mock
from groq import APIStatusError
from src.api_retry import retry_api_call

class TestAPIRetry(unittest.TestCase):

    @patch("src.api_retry.time.sleep")
    def test_successful_request(self, mock_sleep):
        operation = Mock(return_value="success")

        result = retry_api_call(operation)

        self.assertEqual(result, "success")
        operation.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("src.api_retry.time.sleep")
    def test_retry_after_rate_limit(self, mock_sleep):
        operation = Mock(
            side_effect=[
                APIStatusError(
                    "Rate limit",
                    response=Mock(
                        status_code=429,
                        headers={"retry-after": "1"}
                    ),
                    body={}
                ),
                "success"
            ]
        )

        result = retry_api_call(operation)

        self.assertEqual(result, "success")
        self.assertEqual(operation.call_count, 2)
        mock_sleep.assert_called_once_with(1.0)

    @patch("src.api_retry.time.sleep")
    def test_retry_exhaustion(self, mock_sleep):
        error = APIStatusError(
            "Rate limit",
            response=Mock(status_code=429, headers={}),
            body={}
        )

        operation = Mock(side_effect=error)

        with self.assertRaises(APIStatusError):
            retry_api_call(operation)

        self.assertEqual(operation.call_count, 5)
        self.assertEqual(mock_sleep.call_count, 4)

if __name__ == "__main__":
    unittest.main()
