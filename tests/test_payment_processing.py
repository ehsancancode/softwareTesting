import unittest
from unittest import mock
from Payment_Processing import PaymentProcessing


class FakePaymentProcessing:
    def __init__(self):
        self.declined_cards = ["1111222233334444", "9999000099990000"]

    def validate_credit_card(self, details):
        card_number = details.get("card_number", "")
        cvv = details.get("cvv", "")
        return len(card_number) == 16 and len(cvv) == 3

    def process_payment(self, order, payment_method, payment_details):
        if payment_method != "credit_card":
            return "Error: Invalid payment method"

        if not self.validate_credit_card(payment_details):
            return "Error: Invalid credit card details"

        if payment_details["card_number"] in self.declined_cards:
            return "Payment failed, please try again"
        
        return "Payment successful, Order confirmed"


class TestWithFakePaymentGateway(unittest.TestCase):
    def setUp(self):
        self.processor = FakePaymentProcessing()
        self.order = {"total_amount": 100.00}

    def test_fake_payment_success(self):
        details = {
            "card_number": "1234567812345678",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = self.processor.process_payment(self.order, "credit_card", details)
        self.assertEqual(result, "Payment successful, Order confirmed")

    def test_fake_payment_decline(self):
        details = {
            "card_number": "1111222233334444",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        result = self.processor.process_payment(self.order, "credit_card", details)
        self.assertEqual(result, "Payment failed, please try again")

    def test_fake_payment_invalid_card(self):
        details = {
            "card_number": "1234",
            "expiry_date": "12/25",
            "cvv": "1",
        }
        result = self.processor.process_payment(self.order, "credit_card", details)
        self.assertEqual(result, "Error: Invalid credit card details")

#NEW CODE ADDED BY JIMMY UNTIL HERE
class TestPaymentProcessing(unittest.TestCase):
    def setUp(self):
        self.payment_processing = PaymentProcessing()

    def test_validate_payment_method_success(self):
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
        payment_details = {
            "card_number": "1234567812345678",
            "expiry_date": "12/25",
            "cvv": "123",
        }
        with self.assertRaises(ValueError) as context:
            self.payment_processing.validate_payment_method("bitcoin", payment_details)
        self.assertEqual(str(context.exception), "Invalid payment method")

    def test_validate_credit_card_invalid_details(self):
        payment_details = {"card_number": "1234", "expiry_date": "12/25", "cvv": "12"}
        result = self.payment_processing.validate_credit_card(payment_details)
        self.assertFalse(result)

    def test_process_payment_success(self):
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