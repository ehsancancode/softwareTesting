import unittest
from unittest import mock
from Payment_Processing import PaymentProcessing

class TestPaymentProcessing(unittest.TestCase):
    """Unit tests for PaymentProcessing class."""

    def setUp(self):
        self.payment_processing = PaymentProcessing()

    # ---------- Validation Tests ----------
    def test_validate_payment_method_success(self):
        """Valid credit card and supported gateway should pass."""
        payment_details = {
            "card_number": "1234567812345678",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = self.payment_processing.validate_payment_method(
            "credit_card", payment_details
        )
        self.assertTrue(result)

    def test_validate_payment_method_invalid_gateway(self):
        """Unsupported gateway should raise ValueError."""
        payment_details = {
            "card_number": "1234567812345678",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        with self.assertRaises(ValueError) as context:
            self.payment_processing.validate_payment_method("bitcoin", payment_details)
        self.assertEqual(str(context.exception), "Invalid payment method")

    def test_validate_credit_card_invalid_details(self):
        """Invalid card number or CVV should fail validation."""
        payment_details = {"card_number": "1234", "expiry_date": "12/25", "cvv": "12"}
        result = self.payment_processing.validate_credit_card(payment_details)
        self.assertFalse(result)

    # ---------- Payment Process Tests ----------
    def test_process_payment_success(self):
        """Simulated successful payment."""
        order = {"total_amount": 100.00}
        payment_details = {
            "card_number": "1234567812345678",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        with mock.patch.object(
                self.payment_processing, "mock_payment_gateway", return_value={"status": "success"}
        ):
            result = self.payment_processing.process_payment(
                order, "credit_card", payment_details
            )
            self.assertEqual(result, "Payment successful, Order confirmed")

    def test_process_payment_failure(self):
        """Simulated failed payment (e.g. declined card)."""
        order = {"total_amount": 100.00}
        payment_details = {
            "card_number": "1111222233334444",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        with mock.patch.object(
                self.payment_processing, "mock_payment_gateway", return_value={"status": "failure"}
        ):
            result = self.payment_processing.process_payment(
                order, "credit_card", payment_details
            )
            self.assertEqual(result, "Payment failed, please try again")

    def test_process_payment_invalid_method(self):
        """Invalid payment method should trigger error."""
        order = {"total_amount": 100.00}
        payment_details = {
            "card_number": "1234567812345678",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = self.payment_processing.process_payment(order, "bitcoin", payment_details)
        self.assertIn("Error: Invalid payment method", result)

if __name__ == "__main__":
    unittest.main()
